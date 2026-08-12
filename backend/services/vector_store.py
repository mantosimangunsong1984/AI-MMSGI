import joblib
import faiss
import numpy as np
import re

from backend.utils.config import VECTOR_INDEX, VECTOR_METADATA


class VectorStore:

    # =====================================================
    # CONFIG
    # =====================================================

    DEFAULT_DIMENSION = 384

    # -----------------------------------------------------
    # Minimum final similarity score
    # -----------------------------------------------------

    MIN_SIMILARITY_SCORE = 0.30

    # -----------------------------------------------------
    # Relative score margin
    # -----------------------------------------------------

    RELATIVE_SCORE_MARGIN = 0.12

    # -----------------------------------------------------
    # Candidate retrieval
    # -----------------------------------------------------

    CANDIDATE_MULTIPLIER = 5

    MIN_CANDIDATE_K = 15

    # -----------------------------------------------------
    # FINAL SCORE WEIGHTS
    #
    # Semantic tetap menjadi faktor utama.
    #
    # Final Score =
    #
    # 70% Semantic
    # 20% Keyword
    # 10% Evidence
    # -----------------------------------------------------

    SEMANTIC_WEIGHT = 0.70

    KEYWORD_WEIGHT = 0.20

    EVIDENCE_WEIGHT = 0.10

    # -----------------------------------------------------
    # Keyword scoring
    # -----------------------------------------------------

    MAX_KEYWORD_BOOST = 0.40

    # -----------------------------------------------------
    # Neighbor chunk
    # -----------------------------------------------------

    NEIGHBOR_DISTANCE = 1

    NEIGHBOR_SCORE_PENALTY = 0.025

    # =====================================================
    # STOPWORDS
    # =====================================================

    STOPWORDS = {
        "apa",
        "berapa",
        "yang",
        "adalah",
        "bagaimana",
        "siapa",
        "mengapa",
        "kapan",
        "dimana",
        "mana",
        "untuk",
        "dengan",
        "tentang",
        "pada",
        "dari",
        "dalam",
        "dan",
        "atau",
        "ini",
        "itu",
        "ke",
        "di",
        "oleh",
        "sebagai",
        "akan",
        "dapat",
        "bisa",
        "apakah",
        "kebijakan",
        "mengenai",
        "terkait",
        "sebuah",
        "suatu",
        "saya",
        "kami",
        "kita",
        "anda",
        "mereka",
        "boleh",
        "tidak",
        "untuknya",
        "tersebut",
    }

    ANSWER_EVIDENCE_TERMS = {
        "nilai penggantian maksimum",
        "maximum reimbursement",
        "nilai maksimum",
        "maksimum reimbursement",
        "limit penggantian",
        "nilai reimbursement",
        "penggantian maksimum",
        "reimbursement",
    }

    def _calculate_answer_evidence(self, question, metadata):
        question_text = self._normalize_text(question)

        text = self._normalize_text(metadata.get("text", ""))

        score = 0.0
        matches = []

        # =============================================
        # TABLE
        # =============================================

        if "[table" in text:
            score += 0.20
            matches.append("table")

        # =============================================
        # ANSWER TERMS
        # =============================================

        for term in self.ANSWER_EVIDENCE_TERMS:

            if term in text:

                score += 0.20

                matches.append(term)

        # =============================================
        # MONEY / NUMERIC VALUE
        # =============================================

        if re.search(r"\bidr\s?[\d.,]+", text, re.IGNORECASE):
            score += 0.20
            matches.append("currency")

        # =============================================
        # QUESTION INTENT
        # =============================================

        limit_question = any(
            term in question_text
            for term in ["limit", "maksimal", "maksimum", "nominal", "nilai", "berapa"]
        )

        if limit_question:

            if (
                "maximum reimbursement" in text
                or "nilai penggantian maksimum" in text
                or "nilai maksimum" in text
            ):
                score += 0.20

                matches.append("limit-answer")

        return {"score": min(score, 1.0), "matches": list(dict.fromkeys(matches))}

        # =====================================================
        # INIT
        # =====================================================

    def __init__(self, dimension=DEFAULT_DIMENSION):

        self.dimension = dimension

        self.index = faiss.IndexFlatIP(dimension)

        self.metadata = []

        # =================================================
        # IMPORTANT KEYWORDS
        #
        # Keyword yang sangat menentukan intent.
        # =================================================

        self.IMPORTANT_KEYWORDS = {
            "cuti",
            "bpjs",
            "kacamata",
            "manfaat",
            "klaim",
            "reimburse",
            "reimbursement",
            "medical",
            "pengobatan",
            "rawat",
            "inap",
            "asuransi",
            "tunjangan",
            "bonus",
            "gaji",
            "lembur",
            "thr",
            "koperasi",
            "pinjaman",
            "seragam",
            "transport",
            "absensi",
            "kehadiran",
            "izin",
            "sakit",
            "perjalanan",
            "dinas",
            "training",
            "pelatihan",
            "kontrak",
            "resign",
            "mutasi",
            "promosi",
            "kinerja",
            "penilaian",
            "salary",
            "pengunduran",
            "fingerprint",
            "makan",
            # =============================================
            # BENEFIT / LIMIT / REIMBURSEMENT
            # =============================================
            "limit",
            "maksimum",
            "maksimal",
            "penggantian",
        }

        # =================================================
        # GENERIC KEYWORDS
        #
        # Keyword umum yang masih relevan tetapi tidak
        # sekuat IMPORTANT_KEYWORDS.
        # =================================================

        self.GENERIC_KEYWORDS = {
            "biaya",
            "nilai",
            "pengajuan",
            "permintaan",
            "prosedur",
            "proses",
            "syarat",
            "ketentuan",
            "aturan",
            "hak",
            "fasilitas",
            "dokumen",
            "formulir",
            "periode",
            "tanggal",
            "jumlah",
            "besaran",
            "perusahaan",
            "pegawai",
            "karyawan",
            "employee",
            "benefit",
        }

    # =====================================================
    # ADD VECTOR
    # =====================================================

    def add(self, embeddings):

        if not embeddings:

            print("Tidak ada embedding untuk ditambahkan.")

            return

        vectors = []

        for item in embeddings:

            vector = np.asarray(item["embedding"], dtype=np.float32)

            # =============================================
            # VALIDATE DIMENSION
            # =============================================

            if vector.ndim != 1:

                raise ValueError("Embedding harus berupa vector 1 dimensi.")

            if vector.shape[0] != self.dimension:

                raise ValueError(
                    "Dimensi embedding tidak sesuai. "
                    f"Expected={self.dimension}, "
                    f"Actual={vector.shape[0]}"
                )

            vectors.append(vector)

            # =============================================
            # METADATA
            # =============================================

            self.metadata.append(
                {
                    "filename": item.get("filename", ""),
                    "document_name": item.get("document_name", ""),
                    "extension": item.get("extension", ""),
                    "size": item.get("size", 0),
                    "chunk_id": item.get("chunk_id", 0),
                    "text": item.get("text", ""),
                }
            )

        vectors = np.asarray(vectors, dtype=np.float32)

        # =============================================
        # NORMALIZE VECTOR
        #
        # IndexFlatIP akan berfungsi sebagai cosine
        # similarity jika vector sudah normalized.
        # =============================================

        faiss.normalize_L2(vectors)

        # =============================================
        # ADD TO FAISS
        # =============================================

        self.index.add(vectors)

        print("Vector berhasil ditambahkan.")

        print("Vector total:", self.index.ntotal)

        print("Metadata total:", len(self.metadata))

    # =====================================================
    # TOKENIZE QUESTION
    # =====================================================

    def _tokenize(self, text):

        if not text:

            return []

        text = str(text).lower()

        words = re.findall(r"[a-zA-Z0-9À-ÿ]+", text)

        keywords = []

        for word in words:

            if len(word) < 4:

                continue

            if word in self.STOPWORDS:

                continue

            keywords.append(word)

        # Remove duplicate
        return list(dict.fromkeys(keywords))

    # =====================================================
    # NORMALIZE TEXT
    # =====================================================

    def _normalize_text(self, text):

        if not text:

            return ""

        text = str(text).lower()

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # =====================================================
    # GET CHUNK ID
    # =====================================================

    def _get_chunk_id(self, metadata):

        value = metadata.get("chunk_id", 0)

        try:

            return int(value)

        except Exception:

            return 0

    # =====================================================
    # GET DOCUMENT KEY
    # =====================================================

    def _get_document_key(self, metadata):

        return str(metadata.get("document_name", "")).strip().lower()

    # =====================================================
    # PHRASE DETECTION
    # =====================================================

    def _build_phrases(self, keywords):

        phrases = []

        if len(keywords) < 2:

            return phrases

        # =================================================
        # BIGRAM
        # =================================================

        for i in range(len(keywords) - 1):

            phrase = keywords[i] + " " + keywords[i + 1]

            phrases.append(phrase)

        # =================================================
        # SPECIFIC SEMANTIC PHRASES
        # =================================================

        known_phrases = [
            "nilai penggantian",
            "penggantian maksimum",
            "maksimum kacamata",
            "nilai maksimum",
            "biaya penggantian",
            "limit penggantian",
            "maksimum reimbursement",
            "nilai reimbursement",
            "manfaat kacamata",
            "penggantian biaya",
            "pengadaan kacamata",
            "klaim kacamata",
        ]

        keyword_text = " ".join(keywords)

        for phrase in known_phrases:

            if phrase in keyword_text:

                phrases.append(phrase)

        return list(dict.fromkeys(phrases))

    # =====================================================
    # KEYWORD ANALYSIS
    # =====================================================

    def _analyze_keywords(self, question, metadata):

        keywords = self._tokenize(question)

        if not keywords:

            return {
                "keywords": [],
                "important": [],
                "generic": [],
                "document_matches": [],
                "filename_matches": [],
                "text_matches": [],
                "phrase_matches": [],
                "coverage": 0.0,
                "important_coverage": 0.0,
                "boost": 0.0,
            }

        # =================================================
        # PROTECTED KEYWORD SET
        #
        # getattr() digunakan agar aman apabila attribute
        # belum tersedia karena object lama / perubahan
        # konfigurasi.
        # =================================================

        important_keywords = getattr(self, "IMPORTANT_KEYWORDS", set())

        generic_keywords = getattr(self, "GENERIC_KEYWORDS", set())

        document_name = self._normalize_text(metadata.get("document_name", ""))

        filename = self._normalize_text(metadata.get("filename", ""))

        text = self._normalize_text(metadata.get("text", ""))

        important = []

        generic = []

        document_matches = []

        filename_matches = []

        text_matches = []

        # =================================================
        # CLASSIFY KEYWORDS
        # =================================================

        for word in keywords:

            if word in important_keywords:

                important.append(word)

            elif word in generic_keywords:

                generic.append(word)

        # =================================================
        # MATCH DOCUMENT
        # =================================================

        for word in keywords:

            if word in document_name:

                document_matches.append(word)

        # =================================================
        # MATCH FILENAME
        # =================================================

        for word in keywords:

            if word in filename:

                filename_matches.append(word)

        # =================================================
        # MATCH TEXT
        # =================================================

        for word in keywords:

            if word in text:

                text_matches.append(word)

        # =================================================
        # PHRASE MATCH
        # =================================================

        phrases = self._build_phrases(keywords)

        phrase_matches = []

        for phrase in phrases:

            if phrase in text:

                phrase_matches.append(phrase)

        # =================================================
        # COVERAGE
        #
        # Jangan menghitung duplicate match.
        # =================================================

        matched_keywords = list(
            dict.fromkeys(document_matches + filename_matches + text_matches)
        )

        coverage = len(matched_keywords) / len(keywords)

        # =================================================
        # IMPORTANT COVERAGE
        # =================================================

        if important:

            important_matched = [
                word
                for word in important
                if (
                    word in document_matches
                    or word in filename_matches
                    or word in text_matches
                )
            ]

            important_coverage = len(important_matched) / len(important)

        else:

            important_coverage = 0.0

        # =================================================
        # SCORE COMPONENTS
        # =================================================

        boost = 0.0

        # -------------------------------------------------
        # IMPORTANT KEYWORD
        # -------------------------------------------------

        if important:

            boost += important_coverage * 0.22

        # -------------------------------------------------
        # TEXT COVERAGE
        # -------------------------------------------------

        boost += coverage * 0.08

        # -------------------------------------------------
        # DOCUMENT NAME
        # -------------------------------------------------

        document_important_matches = [
            word for word in important if word in document_matches
        ]

        boost += min(len(document_important_matches) * 0.08, 0.16)

        # -------------------------------------------------
        # FILENAME
        # -------------------------------------------------

        filename_important_matches = [
            word for word in important if word in filename_matches
        ]

        boost += min(len(filename_important_matches) * 0.05, 0.10)

        # -------------------------------------------------
        # PHRASE BOOST
        # -------------------------------------------------

        phrase_boost = min(len(phrase_matches) * 0.08, 0.20)

        boost += phrase_boost

        # -------------------------------------------------
        # GENERIC KEYWORD
        # -------------------------------------------------

        generic_matches = [word for word in generic if word in text]

        boost += min(len(generic_matches) * 0.01, 0.03)

        # -------------------------------------------------
        # MAXIMUM BOOST
        # -------------------------------------------------

        boost = min(boost, self.MAX_KEYWORD_BOOST)

        # =================================================
        # DEBUG
        # =================================================

        print()

        print("KEYWORD ANALYSIS")

        print("Keywords:", keywords)

        print("Important:", important)

        print("Generic:", generic)

        print("Document Matches:", document_matches)

        print("Filename Matches:", filename_matches)

        print("Text Matches:", text_matches)

        print("Phrase Matches:", phrase_matches)

        print("Coverage:", round(coverage, 4))

        print("Important Coverage:", round(important_coverage, 4))

        print("Keyword Boost:", round(boost, 4))

        return {
            "keywords": keywords,
            "important": important,
            "generic": generic,
            "document_matches": document_matches,
            "filename_matches": filename_matches,
            "text_matches": text_matches,
            "phrase_matches": phrase_matches,
            "coverage": coverage,
            "important_coverage": important_coverage,
            "boost": float(boost),
        }

    # =====================================================
    # KEYWORD BOOST
    # =====================================================

    def _calculate_keyword_boost(self, question, metadata):

        analysis = self._analyze_keywords(question, metadata)

        matched_keywords = list(
            dict.fromkeys(
                analysis["document_matches"]
                + analysis["filename_matches"]
                + analysis["text_matches"]
            )
        )

        return (analysis["boost"], matched_keywords)



    def _calculate_answer_evidence_score(self, text, question):
        """
        Mengukur apakah chunk mengandung bukti langsung
        untuk menjawab pertanyaan.

        Contoh:
        Question:
            "Berapa limit manfaat kacamata?"

        Evidence:
            "Nilai Penggantian Maksimum"
            "Maximum Reimbursement"
            "IDR 6,000,000"
        """

        if not text or not question:
            return 0.0

        text_lower = text.lower()
        question_lower = question.lower()

        score = 0.0

        # =================================================
        # 1. QUESTION MEMINTA NILAI / NOMINAL
        # =================================================

        value_question_keywords = {
            "berapa",
            "nilai",
            "jumlah",
            "besaran",
            "nominal",
            "limit",
            "maksimum",
            "maksimal",
            "biaya",
        }

        asks_for_value = any(
            keyword in question_lower
            for keyword in value_question_keywords
        )

        if asks_for_value:

            # =================================================
            # 2. INDIKATOR NILAI / LIMIT DI DOKUMEN
            # =================================================

            value_evidence_keywords = {
                "nilai penggantian maksimum",
                "maximum reimbursement",
                "nilai maksimum",
                "maksimum reimbursement",
                "reimbursement",
                "limit",
                "maksimal",
                "maksimum",
            }

            matched_value_evidence = [
                keyword
                for keyword in value_evidence_keywords
                if keyword in text_lower
            ]

            if matched_value_evidence:
                score += 0.60

            # =================================================
            # 3. ADA NOMINAL UANG
            # =================================================

            import re

            money_patterns = [
                r"idr\s*[\d\.,]+",
                r"rp\.?\s*[\d\.,]+",
                r"rp\s*[\d\.,]+",
                r"\b\d{1,3}(?:[\.,]\d{3})+(?:[\.,]\d+)?\b",
            ]

            has_money = any(
                re.search(pattern, text_lower)
                for pattern in money_patterns
            )

            if has_money:
                score += 0.40

        return max(0.0, min(score, 1.0))



    # =====================================================
    # CALCULATE FINAL SCORE
    # =====================================================

    def _calculate_final_score(self, raw_score, analysis, text="", question=""):

        # =================================================
        # SEMANTIC SCORE
        # =================================================

        semantic_score = max(
            0.0,
            min(float(raw_score), 1.0)
        )

        # =================================================
        # KEYWORD SCORE
        # =================================================

        if self.MAX_KEYWORD_BOOST > 0:

            keyword_score = (
                analysis["boost"] /
                self.MAX_KEYWORD_BOOST
            )

        else:

            keyword_score = 0.0

        keyword_score = max(
            0.0,
            min(keyword_score, 1.0)
        )

        # =================================================
        # EVIDENCE SCORE
        # =================================================

        important_component = (
            analysis["important_coverage"] * 0.60
        )

        coverage_component = (
            analysis["coverage"] * 0.25
        )

        phrase_component = (
            min(len(analysis["phrase_matches"]), 2)
            / 2
            * 0.15
        )

        evidence_score = (
            important_component
            + coverage_component
            + phrase_component
        )

        evidence_score = max(
            0.0,
            min(evidence_score, 1.0)
        )

        # =================================================
        # ANSWER EVIDENCE SCORE
        # =================================================

        answer_evidence_score = (
            self._calculate_answer_evidence_score(
                text,
                question
            )
        )

        # =================================================
        # FINAL SCORE
        # =================================================

        final_score = (
            semantic_score * 0.45
            + keyword_score * 0.20
            + evidence_score * 0.20
            + answer_evidence_score * 0.15
        )

        return {
            "semantic_score": semantic_score,
            "keyword_score": keyword_score,
            "evidence_score": evidence_score,
            "answer_evidence_score": answer_evidence_score,
            "final_score": max(
                0.0,
                min(final_score, 1.0)
            )
        }

    # =====================================================
    # FIND NEIGHBOR CHUNKS
    # =====================================================

    def _find_neighbor_chunks(self, metadata, distance=None):

        if distance is None:

            distance = self.NEIGHBOR_DISTANCE

        document_key = self._get_document_key(metadata)

        chunk_id = self._get_chunk_id(metadata)

        neighbors = []

        for index, item in enumerate(self.metadata):

            if item is metadata:

                continue

            other_document = self._get_document_key(item)

            if other_document != document_key:

                continue

            other_chunk_id = self._get_chunk_id(item)

            chunk_distance = abs(other_chunk_id - chunk_id)

            if chunk_distance <= distance:

                neighbors.append(
                    {"metadata": item, "index": index, "distance": chunk_distance}
                )

        return neighbors

    # =====================================================
    # SEARCH
    # =====================================================

    def search(self, query_vector, question="", top_k=3):

        print()

        print("=" * 80)

        print("VECTOR STORE SEARCH")

        print("=" * 80)

        print("Question:", repr(question))

        print("Requested Top K:", top_k)

        # =================================================
        # EMPTY INDEX
        # =================================================

        if self.index.ntotal == 0:

            print("Vector index kosong.")

            print("=" * 80)

            return []

        # =================================================
        # METADATA CHECK
        # =================================================

        if len(self.metadata) != self.index.ntotal:

            raise RuntimeError(
                "Jumlah metadata tidak sama "
                "dengan jumlah vector. "
                f"Vector={self.index.ntotal}, "
                f"Metadata={len(self.metadata)}"
            )

        # =================================================
        # VALIDATE TOP K
        # =================================================

        try:

            top_k = int(top_k)

        except Exception:

            top_k = 3

        if top_k <= 0:

            top_k = 3

        # =================================================
        # RETRIEVE MORE CANDIDATES
        # =================================================

        candidate_k = max(top_k * self.CANDIDATE_MULTIPLIER, self.MIN_CANDIDATE_K)

        candidate_k = min(candidate_k, self.index.ntotal)

        # =================================================
        # QUERY VECTOR
        # =================================================

        query = np.asarray(query_vector, dtype=np.float32)

        if query.ndim == 1:

            query = np.expand_dims(query, axis=0)

        if query.ndim != 2:

            raise ValueError("Query vector harus berupa " "array 1D atau 2D.")

        if query.shape[1] != self.dimension:

            raise ValueError(
                "Dimensi query vector tidak sesuai. "
                f"Expected={self.dimension}, "
                f"Actual={query.shape[1]}"
            )

        # =================================================
        # NORMALIZE QUERY
        # =================================================

        faiss.normalize_L2(query)

        # =================================================
        # FAISS SEARCH
        # =================================================

        scores, indexes = self.index.search(query, candidate_k)

        print("FAISS Candidate Count:", candidate_k)

        print("Total Vector:", self.index.ntotal)

        # =================================================
        # QUESTION KEYWORDS
        # =================================================

        keywords = self._tokenize(question)

        print("Keywords:", keywords)

        # =================================================
        # PRIMARY CANDIDATES
        # =================================================

        primary_candidates = []

        for raw_score, idx in zip(scores[0], indexes[0]):

            if idx == -1:

                continue

            idx = int(idx)

            metadata = self.metadata[idx]

            raw_score = float(raw_score)

            # =============================================
            # KEYWORD ANALYSIS
            # =============================================

            analysis = self._analyze_keywords(question, metadata)

            # =============================================
            # SCORE CALCULATION
            # =============================================

            # score_data = self._calculate_final_score(raw_score, analysis)

            score_data = self._calculate_final_score(
                raw_score,
                analysis,
                text=metadata.get("text", ""),
                question=question,
            )

            print("\nANSWER EVIDENCE DEBUG")
            print("Question              :", question)
            print("Answer Evidence Score :", score_data["answer_evidence_score"])

            primary_candidates.append(
                {
                    "index": idx,
                    "metadata": metadata,
                    "raw_score": raw_score,
                    "semantic_score": score_data["semantic_score"],
                    "keyword_score": score_data["keyword_score"],
                    "evidence_score": score_data["evidence_score"],
                    "boost": analysis["boost"],
                    "analysis": analysis,
                    "score": score_data["final_score"],
                    "primary": True,
                    "neighbor": False,
                    "distance": 0,
                }
            )

        # =================================================
        # SORT PRIMARY
        # =================================================

        primary_candidates.sort(
            key=lambda item: (
                item["score"],
                item["raw_score"],
                item["analysis"]["important_coverage"],
                item["analysis"]["coverage"],
            ),
            reverse=True,
        )

        # =================================================
        # NEIGHBOR RETRIEVAL
        # =================================================

        seed_count = min(max(top_k * 3, 6), len(primary_candidates))

        seed_candidates = primary_candidates[:seed_count]

        context_candidates = []

        seen_indexes = set()

        # =================================================
        # ADD PRIMARY
        # =================================================

        for item in seed_candidates:

            index = item["index"]

            if index in seen_indexes:

                continue

            seen_indexes.add(index)

            context_candidates.append(item)

        # =================================================
        # ADD NEIGHBORS
        # =================================================

        for primary in seed_candidates:

            neighbors = self._find_neighbor_chunks(primary["metadata"])

            for neighbor in neighbors:

                neighbor_index = neighbor["index"]

                if neighbor_index in seen_indexes:

                    continue

                neighbor_metadata = neighbor["metadata"]


                print("\n===== NEIGHBOR DEBUG =====")
                print("Neighbor keys :", list(neighbor.keys()))
                print("Metadata keys :", list(neighbor_metadata.keys()))

                print("Text :", neighbor_metadata.get("text", "[NO TEXT]"))
                print("==========================")

                # print("\n===== NEIGHBOR DEBUG =====")
                # print("Neighbor keys   :", neighbor.keys())
                # print("Metadata keys   :", neighbor_metadata.keys())
                # print("Metadata        :", neighbor_metadata)
                # print("==========================")
                # print("\n" + "=" * 80)
                # print("DEBUG NEIGHBOR METADATA")
                # print("=" * 80)
                # print(neighbor_metadata)
                # print("=" * 80)

                analysis = self._analyze_keywords(question, neighbor_metadata)

                distance = neighbor["distance"]

                neighbor_raw_score = primary["raw_score"] * max(
                    0.0, 1.0 - (self.NEIGHBOR_SCORE_PENALTY * distance)
                )

                # score_data = self._calculate_final_score(neighbor_raw_score, analysis)

                score_data = self._calculate_final_score(
                neighbor_raw_score,
                analysis,
                text=neighbor_metadata.get("text", ""),
                question=question
                )

                neighbor_penalty = self.NEIGHBOR_SCORE_PENALTY * distance

                final_score = score_data["final_score"] - neighbor_penalty

                final_score = max(0.0, final_score)

                context_candidates.append(
                    {
                        "index": neighbor_index,
                        "metadata": neighbor_metadata,
                        "raw_score": float(neighbor_raw_score),
                        "semantic_score": score_data["semantic_score"],
                        "keyword_score": score_data["keyword_score"],
                        "evidence_score": score_data["evidence_score"],
                        "boost": analysis["boost"],
                        "analysis": analysis,
                        "score": float(final_score),
                        "primary": False,
                        "neighbor": True,
                        "distance": distance,
                    }
                )

                seen_indexes.add(neighbor_index)

        # =================================================
        # ADD REMAINING PRIMARY CANDIDATES
        # =================================================

        for item in primary_candidates:

            index = item["index"]

            if index in seen_indexes:

                continue

            analysis = item["analysis"]

            if analysis["important_coverage"] > 0.0 or analysis["coverage"] >= 0.50:

                context_candidates.append(item)

                seen_indexes.add(index)

        # =================================================
        # DEDUPLICATE
        # =================================================

        unique_candidates = {}

        for item in context_candidates:

            index = item["index"]

            current = unique_candidates.get(index)

            if current is None:

                unique_candidates[index] = item

                continue

            if item["primary"] and not current["primary"]:

                unique_candidates[index] = item

                continue

            if item["score"] > current["score"]:

                unique_candidates[index] = item

        context_candidates = list(unique_candidates.values())

        # =================================================
        # SORT CONTEXT
        # =================================================

        context_candidates.sort(
            key=lambda item: (
                item["score"],
                item["raw_score"],
                item["analysis"]["important_coverage"],
                item["analysis"]["coverage"],
                len(item["analysis"]["phrase_matches"]),
                1 if item["primary"] else 0,
                -item["distance"],
            ),
            reverse=True,
        )

        # =================================================
        # DEBUG CONTEXT
        # =================================================

        print()

        print("=" * 80)

        print("CONTEXT CANDIDATES")

        print("=" * 80)

        for rank, item in enumerate(context_candidates, start=1):

            metadata = item["metadata"]

            analysis = item["analysis"]

            print()

            print(f"Context #{rank}")

            print("-" * 60)

            print("Document:", metadata.get("document_name", ""))

            print("Chunk:", metadata.get("chunk_id", 0))

            print("Raw / Semantic Score:", round(item["raw_score"], 4))

            print("Semantic Score:", round(item["semantic_score"], 4))

            print("Keyword Score:", round(item["keyword_score"], 4))

            print("Evidence Score:", round(item["evidence_score"], 4))

            print("Keyword Boost:", round(item["boost"], 4))

            print("Final Score:", round(item["score"], 4))

            print("Coverage:", round(analysis["coverage"], 4))

            print("Important Coverage:", round(analysis["important_coverage"], 4))

            print(
                "Keywords:",
                list(
                    dict.fromkeys(
                        analysis["document_matches"]
                        + analysis["filename_matches"]
                        + analysis["text_matches"]
                    )
                ),
            )

            print("Phrase Matches:", analysis["phrase_matches"])

            print("Primary:", item["primary"])

            print("Neighbor:", item["neighbor"])

            print("Distance:", item["distance"])

            print("Preview:", metadata.get("text", "")[:300])

        # =================================================
        # NO CANDIDATE
        # =================================================

        if not context_candidates:

            print("Tidak ada candidate.")

            print("=" * 80)

            return []

        # =================================================
        # BEST SCORE
        # =================================================

        best_score = context_candidates[0]["score"]

        # =================================================
        # RELATIVE THRESHOLD
        # =================================================

        relative_threshold = best_score - self.RELATIVE_SCORE_MARGIN

        # =================================================
        # ABSOLUTE THRESHOLD
        # =================================================

        threshold = max(self.MIN_SIMILARITY_SCORE, relative_threshold)

        print()

        print(f"Best Score         : " f"{best_score:.4f}")

        print(f"Minimum Score      : " f"{self.MIN_SIMILARITY_SCORE:.4f}")

        print(f"Relative Threshold : " f"{relative_threshold:.4f}")

        print(f"Final Threshold    : " f"{threshold:.4f}")

        print("=" * 80)

        # =================================================
        # FILTER
        # =================================================

        results = []

        for rank, item in enumerate(context_candidates, start=1):

            metadata = item["metadata"]

            score = item["score"]

            raw_score = item["raw_score"]

            boost = item["boost"]

            analysis = item["analysis"]

            matched_keywords = list(
                dict.fromkeys(
                    analysis["document_matches"]
                    + analysis["filename_matches"]
                    + analysis["text_matches"]
                )
            )

            print()

            print(f"Context Candidate #{rank}")

            print("Document:", metadata.get("document_name", ""))

            print("Chunk:", metadata.get("chunk_id", 0))

            print("Raw Score:", round(raw_score, 4))

            print("Semantic Score:", round(item["semantic_score"], 4))

            print("Keyword Score:", round(item["keyword_score"], 4))

            print("Evidence Score:", round(item["evidence_score"], 4))

            print("Boost:", round(boost, 4))

            print("Final:", round(score, 4))

            print("Keywords:", matched_keywords)

            print("Phrase Matches:", analysis["phrase_matches"])

            print("Coverage:", round(analysis["coverage"], 4))

            print("Important Coverage:", round(analysis["important_coverage"], 4))

            print("Primary:", item["primary"])

            print("Neighbor:", item["neighbor"])

            print("Distance:", item["distance"])

            print("Preview:", metadata.get("text", "")[:300])

            # =================================================
            # SCORE FILTER
            # =================================================

            if score < threshold:

                strong_evidence = (
                    analysis["important_coverage"] >= 0.75
                    or analysis["coverage"] >= 0.75
                    or len(analysis["phrase_matches"]) >= 2
                )

                if not strong_evidence:

                    print(">>> SKIP - score terlalu rendah")

                    continue

                print(">>> KEEP - strong evidence")

            # =================================================
            # BUILD RESULT
            # =================================================

            result = metadata.copy()

            result["score"] = round(score, 4)

            result["raw_score"] = round(raw_score, 4)

            result["semantic_score"] = round(item["semantic_score"], 4)

            result["keyword_score"] = round(item["keyword_score"], 4)

            result["evidence_score"] = round(item["evidence_score"], 4)

            result["keyword_boost"] = round(boost, 4)

            result["matched_keywords"] = matched_keywords

            result["phrase_matches"] = analysis["phrase_matches"]

            result["keyword_coverage"] = round(analysis["coverage"], 4)

            result["important_keyword_coverage"] = round(
                analysis["important_coverage"], 4
            )

            result["neighbor"] = item["neighbor"]

            result["neighbor_distance"] = item["distance"]

            results.append(result)

        # =================================================
        # FINAL RANKING
        # =================================================

        results.sort(
            key=lambda result: (
                result["score"],
                result["raw_score"],
                result["important_keyword_coverage"],
                result["keyword_coverage"],
                len(result["phrase_matches"]),
            ),
            reverse=True,
        )

        # =================================================
        # LIMIT TOP K
        # =================================================

        results = results[:top_k]

        # =================================================
        # RESULT SUMMARY
        # =================================================

        print()

        print("=" * 80)

        print("FINAL SEARCH RESULT")

        print("=" * 80)

        print("Result Count:", len(results))

        for i, result in enumerate(results, start=1):

            print()

            print(
                f"{i}. "
                f"{result.get('document_name', '')} "
                f"/ "
                f"{result.get('chunk_id', 0)}"
            )

            print(f"   Semantic Score : " f"{result['semantic_score']}")

            print(f"   Keyword Score  : " f"{result['keyword_score']}")

            print(f"   Evidence Score : " f"{result['evidence_score']}")

            print(f"   Final Score    : " f"{result['score']}")

            print(f"   Keyword Boost  : " f"{result['keyword_boost']}")

            print(f"   Coverage       : " f"{result['keyword_coverage']}")

            print(f"   Important Cov. : " f"{result['important_keyword_coverage']}")

            print(f"   Neighbor       : " f"{result['neighbor']}")

        print("=" * 80)

        return results

    # =====================================================
    # SAVE
    # =====================================================

    def save(self):

        VECTOR_INDEX.parent.mkdir(parents=True, exist_ok=True)

        VECTOR_METADATA.parent.mkdir(parents=True, exist_ok=True)

        # =================================================
        # VALIDATE BEFORE SAVE
        # =================================================

        if self.index.ntotal != len(self.metadata):

            raise RuntimeError(
                "Tidak dapat save VectorStore. "
                "Jumlah vector dan metadata tidak sama."
            )

        # =================================================
        # SAVE FAISS
        # =================================================

        faiss.write_index(self.index, str(VECTOR_INDEX))

        # =================================================
        # SAVE METADATA
        # =================================================

        joblib.dump(self.metadata, VECTOR_METADATA)

        print()

        print("=" * 60)

        print("VECTOR STORE SAVED")

        print("=" * 60)

        print("Index    :", VECTOR_INDEX)

        print("Metadata :", VECTOR_METADATA)

        print("Vectors  :", self.index.ntotal)

        print("Metadata :", len(self.metadata))

        print("=" * 60)

    # =====================================================
    # LOAD
    # =====================================================

    def load(self):

        print()

        print("=" * 60)

        print("VECTOR STORE LOAD")

        print("=" * 60)

        print("VECTOR_INDEX    :", VECTOR_INDEX)

        print("VECTOR_METADATA :", VECTOR_METADATA)

        print("INDEX EXISTS    :", VECTOR_INDEX.exists())

        print("META EXISTS     :", VECTOR_METADATA.exists())

        print("=" * 60)

        # =================================================
        # FILE CHECK
        # =================================================

        if not VECTOR_INDEX.exists():

            print("Index tidak ditemukan.")

            return False

        if not VECTOR_METADATA.exists():

            print("Metadata tidak ditemukan.")

            return False

        # =================================================
        # LOAD INDEX
        # =================================================

        try:

            loaded_index = faiss.read_index(str(VECTOR_INDEX))

        except Exception as e:

            print("Gagal membaca FAISS index:")

            print(repr(e))

            return False

        # =================================================
        # DIMENSION CHECK
        # =================================================

        if loaded_index.d != self.dimension:

            raise RuntimeError(
                "Dimensi FAISS index tidak sesuai. "
                f"Expected={self.dimension}, "
                f"Actual={loaded_index.d}"
            )

        # =================================================
        # LOAD METADATA
        # =================================================

        try:

            metadata = joblib.load(VECTOR_METADATA)

        except Exception as e:

            print("Gagal membaca metadata:")

            print(repr(e))

            return False

        # =================================================
        # VALIDATE METADATA
        # =================================================

        if not isinstance(metadata, list):

            raise RuntimeError("Format metadata tidak valid.")

        # =================================================
        # VALIDATE VECTOR / METADATA
        # =================================================

        if loaded_index.ntotal != len(metadata):

            raise RuntimeError(
                "Vector dan metadata tidak sinkron. "
                f"Vector={loaded_index.ntotal}, "
                f"Metadata={len(metadata)}"
            )

        # =================================================
        # APPLY
        # =================================================

        self.index = loaded_index

        self.metadata = metadata

        print("Vector index berhasil dimuat.")

        print("Dimension      :", self.index.d)

        print("Total Vector   :", self.index.ntotal)

        print("Total Metadata :", len(self.metadata))

        print("=" * 60)

        return True

    # =====================================================
    # EMPTY
    # =====================================================

    def is_empty(self):

        return self.index.ntotal == 0
