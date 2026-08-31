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
    # Semantic          = 50%
    # Keyword           = 20%
    # Evidence          = 15%
    # Answer Evidence   = 15%
    #
    # Total              = 100%
    # -----------------------------------------------------

    SEMANTIC_WEIGHT = 0.50
    KEYWORD_WEIGHT = 0.20
    EVIDENCE_WEIGHT = 0.15
    ANSWER_EVIDENCE_WEIGHT = 0.15

    # -----------------------------------------------------
    # Topic ranking adjustment
    # -----------------------------------------------------

    TOPIC_BOOST = 0.05
    DOCUMENT_TOPIC_BOOST = 0.08

    # -----------------------------------------------------
    # Keyword scoring
    # -----------------------------------------------------

    MAX_KEYWORD_BOOST = 0.40

    # -----------------------------------------------------
    # Neighbor chunk
    # -----------------------------------------------------

    NEIGHBOR_DISTANCE = 1
    NEIGHBOR_SCORE_PENALTY = 0.025

    # -----------------------------------------------------
    # Value / limit question
    # -----------------------------------------------------

    VALUE_QUESTION_BOOST = 0.05

    # -----------------------------------------------------
    # Topic context
    # -----------------------------------------------------

    TOPIC_ANSWER_BOOST = 0.10
    TOPIC_MISMATCH_PENALTY = 0.10

    KACAMATA_CONTEXT_BOOST = 0.08
    KACAMATA_CONTEXT_PENALTY = 0.08

    # -----------------------------------------------------
    # Answer-bearing table / money
    # -----------------------------------------------------

    TABLE_ANSWER_BOOST = 0.10
    MONEY_ANSWER_BOOST = 0.20

    # -----------------------------------------------------
    # Generic answer penalty
    #
    # Untuk query kacamata:
    # reimbursement + money tanpa konteks kacamata
    # tidak boleh dianggap jawaban kuat.
    # -----------------------------------------------------

    GENERIC_ANSWER_PENALTY = 0.20

    # -----------------------------------------------------
    # Neighbor inherited topic
    #
    # Jika chunk tabel tidak mengandung kata kacamata,
    # tetapi chunk sebelumnya/sesudahnya adalah chunk kacamata,
    # context dapat diwariskan.
    # -----------------------------------------------------

    INHERITED_TOPIC_BOOST = 0.08

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

    # =====================================================
    # ANSWER EVIDENCE TERMS
    # =====================================================

    ANSWER_EVIDENCE_TERMS = {
        "nilai penggantian maksimum",
        "maximum reimbursement",
        "nilai maksimum",
        "maksimum reimbursement",
        "limit penggantian",
        "nilai reimbursement",
        "penggantian maksimum",
        "reimbursement",
        "maksimal reimbursement",
        "batas reimbursement",
        "batas penggantian",
        "nilai manfaat",
        "manfaat kacamata",
        "nilai manfaat kacamata",
    }

    # =====================================================
    # IMPORTANT KEYWORDS
    # =====================================================

    IMPORTANT_KEYWORDS = {
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

        # Benefit / limit / reimbursement
        "limit",
        "maksimum",
        "maksimal",
        "penggantian",
        "nominal",
        "besaran",
    }

    # =====================================================
    # GENERIC KEYWORDS
    # =====================================================

    GENERIC_KEYWORDS = {
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
    # TOPIC KEYWORDS
    # =====================================================

    TOPIC_KEYWORDS = {

        "kacamata": [
            "kacamata",
            "kaca mata",
            "spectacles",
            "spectacle",
            "glasses",
            "lensa",
            "frame",
        ],

        "cuti": [
            "cuti",
            "izin cuti",
            "cuti tahunan",
            "cuti panjang",
        ],

        "perjalanan_dinas": [
            "perjalanan dinas",
            "dinas",
            "business trip",
            "travel",
            "akomodasi",
            "hotel",
            "tiket pesawat",
        ],

        "medical": [
            "medical",
            "kesehatan",
            "rawat",
            "rumah sakit",
            "pengobatan",
            "reimbursement medis",
        ],

        "benefit": [
            "benefit",
            "manfaat",
            "tunjangan",
            "fasilitas",
            "reimbursement",
            "penggantian",
        ],
    }

    # =====================================================
    # DOCUMENT TOPIC KEYWORDS
    # =====================================================

    DOCUMENT_TOPIC_KEYWORDS = {

        "kacamata": [
            "kacamata",
            "kaca mata",
            "spectacles",
            "glasses",
        ],

        "cuti": [
            "cuti",
        ],

        "perjalanan_dinas": [
            "perjalanan dinas",
        ],

        "medical": [
            "medical",
            "kesehatan",
            "pengobatan",
        ],

        "benefit": [
            "benefit",
            "manfaat",
        ],
    }

    # =====================================================
    # KACAMATA TERMS
    # =====================================================

    KACAMATA_TERMS = (
        "kacamata",
        "kaca mata",
        "spectacles",
        "spectacle",
        "glasses",
    )

    # =====================================================
    # VALUE TERMS
    # =====================================================

    VALUE_TERMS = (
        "berapa",
        "nilai",
        "jumlah",
        "besaran",
        "nominal",
        "limit",
        "maksimum",
        "maksimal",
        "biaya",
        "harga",
    )

    # =====================================================
    # STRONG VALUE TERMS
    # =====================================================

    STRONG_VALUE_TERMS = (
        "nilai penggantian maksimum",
        "maximum reimbursement",
        "nilai maksimum",
        "maksimum reimbursement",
        "limit penggantian",
        "penggantian maksimum",
        "batas reimbursement",
        "batas penggantian",
        "nilai manfaat",
        "manfaat kacamata",
        "nilai manfaat kacamata",
    )

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self, dimension=DEFAULT_DIMENSION):

        self.dimension = dimension

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.metadata = []

    # =====================================================
    # NORMALIZE TEXT
    # =====================================================

    def _normalize_text(self, text):

        if not text:
            return ""

        text = str(text).lower()

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # =====================================================
    # TOKENIZE QUESTION
    # =====================================================

    def _tokenize(self, text):

        if not text:
            return []

        text = self._normalize_text(
            text
        )

        words = re.findall(
            r"[a-zA-Z0-9À-ÿ]+",
            text
        )

        keywords = []

        for word in words:

            if len(word) < 4:
                continue

            if word in self.STOPWORDS:
                continue

            keywords.append(
                word
            )

        return list(
            dict.fromkeys(
                keywords
            )
        )

    # =====================================================
    # GET CHUNK ID
    # =====================================================

    def _get_chunk_id(self, metadata):

        value = metadata.get(
            "chunk_id",
            0
        )

        try:
            return int(value)

        except Exception:
            return 0

    # =====================================================
    # GET DOCUMENT KEY
    # =====================================================

    def _get_document_key(self, metadata):

        return str(
            metadata.get(
                "document_name",
                ""
            )
        ).strip().lower()

    # =====================================================
    # ADD VECTOR
    # =====================================================

    def add(self, embeddings):

        if not embeddings:

            print(
                "Tidak ada embedding untuk ditambahkan."
            )

            return

        vectors = []

        for item in embeddings:

            vector = np.asarray(
                item["embedding"],
                dtype=np.float32
            )

            if vector.ndim != 1:

                raise ValueError(
                    "Embedding harus berupa vector 1 dimensi."
                )

            if vector.shape[0] != self.dimension:

                raise ValueError(
                    "Dimensi embedding tidak sesuai. "
                    f"Expected={self.dimension}, "
                    f"Actual={vector.shape[0]}"
                )

            vectors.append(
                vector
            )

            self.metadata.append(
                {
                    "filename": item.get(
                        "filename",
                        ""
                    ),

                    "document_name": item.get(
                        "document_name",
                        ""
                    ),

                    "extension": item.get(
                        "extension",
                        ""
                    ),

                    "size": item.get(
                        "size",
                        0
                    ),

                    "chunk_id": item.get(
                        "chunk_id",
                        0
                    ),

                    "text": item.get(
                        "text",
                        ""
                    ),
                }
            )

        vectors = np.asarray(
            vectors,
            dtype=np.float32
        )

        faiss.normalize_L2(
            vectors
        )

        self.index.add(
            vectors
        )

        print(
            "Vector berhasil ditambahkan."
        )

        print(
            "Vector total:",
            self.index.ntotal
        )

        print(
            "Metadata total:",
            len(self.metadata)
        )

    # =====================================================
    # BUILD PHRASES
    # =====================================================

    def _build_phrases(self, keywords):

        phrases = []

        if len(keywords) < 2:
            return phrases

        # -------------------------------------------------
        # Bigram
        # -------------------------------------------------

        for i in range(
            len(keywords) - 1
        ):

            phrase = (
                keywords[i]
                + " "
                + keywords[i + 1]
            )

            phrases.append(
                phrase
            )

        # -------------------------------------------------
        # Specific semantic phrases
        # -------------------------------------------------

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

            "nilai manfaat",

            "nilai manfaat kacamata",

            "manfaat reimbursement",

        ]

        keyword_text = " ".join(
            keywords
        )

        for phrase in known_phrases:

            if phrase in keyword_text:

                phrases.append(
                    phrase
                )

        return list(
            dict.fromkeys(
                phrases
            )
        )

    # =====================================================
    # KEYWORD ANALYSIS
    # =====================================================

    def _analyze_keywords(
        self,
        question,
        metadata
    ):

        keywords = self._tokenize(
            question
        )

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

        important_keywords = getattr(
            self,
            "IMPORTANT_KEYWORDS",
            set()
        )

        generic_keywords = getattr(
            self,
            "GENERIC_KEYWORDS",
            set()
        )

        document_name = self._normalize_text(
            metadata.get(
                "document_name",
                ""
            )
        )

        filename = self._normalize_text(
            metadata.get(
                "filename",
                ""
            )
        )

        text = self._normalize_text(
            metadata.get(
                "text",
                ""
            )
        )

        important = []
        generic = []

        document_matches = []
        filename_matches = []
        text_matches = []

        # -------------------------------------------------
        # Classify
        # -------------------------------------------------

        for word in keywords:

            if word in important_keywords:

                important.append(
                    word
                )

            elif word in generic_keywords:

                generic.append(
                    word
                )

        # -------------------------------------------------
        # Document
        # -------------------------------------------------

        for word in keywords:

            if word in document_name:

                document_matches.append(
                    word
                )

        # -------------------------------------------------
        # Filename
        # -------------------------------------------------

        for word in keywords:

            if word in filename:

                filename_matches.append(
                    word
                )

        # -------------------------------------------------
        # Text
        # -------------------------------------------------

        for word in keywords:

            if word in text:

                text_matches.append(
                    word
                )

        # -------------------------------------------------
        # Phrase
        # -------------------------------------------------

        phrases = self._build_phrases(
            keywords
        )

        phrase_matches = []

        for phrase in phrases:

            if phrase in text:

                phrase_matches.append(
                    phrase
                )

        # -------------------------------------------------
        # Coverage
        # -------------------------------------------------

        matched_keywords = list(
            dict.fromkeys(
                document_matches
                + filename_matches
                + text_matches
            )
        )

        coverage = (
            len(matched_keywords)
            / len(keywords)
        )

        # -------------------------------------------------
        # Important coverage
        # -------------------------------------------------

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

            important_coverage = (
                len(important_matched)
                / len(important)
            )

        else:

            important_coverage = 0.0

        # -------------------------------------------------
        # Boost
        # -------------------------------------------------

        boost = 0.0

        if important:

            boost += (
                important_coverage
                * 0.22
            )

            boost += (
            coverage
            * 0.08
        )

        document_important_matches = [

            word

            for word in important

            if word in document_matches
        ]

        boost += min(
            len(
                document_important_matches
            ) * 0.08,
            0.16
        )

        filename_important_matches = [

            word

            for word in important

            if word in filename_matches
        ]

        boost += min(
            len(
                filename_important_matches
            ) * 0.05,
            0.10
        )

        phrase_boost = min(
            len(phrase_matches)
            * 0.08,
            0.20
        )

        boost += phrase_boost

        generic_matches = [

            word

            for word in generic

            if word in text
        ]

        boost += min(
            len(generic_matches)
            * 0.01,
            0.03
        )

        boost = min(
            boost,
            self.MAX_KEYWORD_BOOST
        )

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
    # DETECT QUERY TOPICS
    # =====================================================

    def _detect_query_topics(
        self,
        query
    ):

        query_lower = self._normalize_text(
            query
        )

        topics = []

        for topic, keywords in self.TOPIC_KEYWORDS.items():

            for keyword in keywords:

                if keyword in query_lower:

                    topics.append(
                        topic
                    )

                    break

        return list(
            dict.fromkeys(
                topics
            )
        )

    # =====================================================
    # CALCULATE TOPIC SCORE
    # =====================================================

    def _calculate_topic_score(
        self,
        query,
        document_text,
        metadata=None
    ):

        topics = self._detect_query_topics(
            query
        )

        if not topics:

            return 0.0, []

        text = self._normalize_text(
            document_text
        )

        filename = ""
        document_name = ""

        if metadata:

            filename = self._normalize_text(
                metadata.get(
                    "filename",
                    ""
                )
            )

            document_name = self._normalize_text(
                metadata.get(
                    "document_name",
                    ""
                )
            )

        searchable_text = (
            f"{filename} "
            f"{document_name} "
            f"{text}"
        )

        matched_topics = []

        for topic in topics:

            keywords = self.TOPIC_KEYWORDS.get(
                topic,
                []
            )

            for keyword in keywords:

                if keyword in searchable_text:

                    matched_topics.append(
                        topic
                    )

                    break

        if not matched_topics:

            return 0.0, []

        score = (
            len(matched_topics)
            / len(topics)
        )

        return score, matched_topics

    # =====================================================
    # TOPIC CONTEXT SCORE
    # =====================================================

    def _calculate_topic_context_score(
        self,
        query,
        metadata
    ):

        topics = self._detect_query_topics(
            query
        )

        if not topics or not metadata:

            return 0.0, []

        text = self._normalize_text(
            metadata.get(
                "text",
                ""
            )
        )

        filename = self._normalize_text(
            metadata.get(
                "filename",
                ""
            )
        )

        document_name = self._normalize_text(
            metadata.get(
                "document_name",
                ""
            )
        )

        searchable_text = (
            f"{filename} "
            f"{document_name} "
            f"{text}"
        )

        matched_topics = []

        for topic in topics:

            topic_keywords = (
                self.TOPIC_KEYWORDS.get(
                    topic,
                    []
                )
            )

            if any(
                keyword in searchable_text
                for keyword in topic_keywords
            ):

                matched_topics.append(
                    topic
                )

        score = (
            len(matched_topics)
            / len(topics)
            if topics
            else 0.0
        )

        return score, matched_topics

    # =====================================================
    # KACAMATA CONTEXT SCORE
    # =====================================================

    def _calculate_kacamata_context_score(
        self,
        query,
        metadata
    ):

        query_topics = self._detect_query_topics(
            query
        )

        if (
            "kacamata" not in query_topics
            or not metadata
        ):

            return 0.0, False

        text = self._normalize_text(
            metadata.get(
                "text",
                ""
            )
        )

        filename = self._normalize_text(
            metadata.get(
                "filename",
                ""
            )
        )

        document_name = self._normalize_text(
            metadata.get(
                "document_name",
                ""
            )
        )

        text_has_kacamata = any(
            term in text
            for term in self.KACAMATA_TERMS
        )

        filename_has_kacamata = any(
            term in filename
            for term in self.KACAMATA_TERMS
        )

        document_has_kacamata = any(
            term in document_name
            for term in self.KACAMATA_TERMS
        )

        has_context = (
            text_has_kacamata
            or filename_has_kacamata
            or document_has_kacamata
        )

        return (
            1.0 if has_context else 0.0,
            has_context
        )

    # =====================================================
    # DOCUMENT TOPIC SCORE
    # =====================================================

    def _calculate_document_topic_score(
        self,
        query,
        metadata
    ):

        topics = self._detect_query_topics(
            query
        )

        if not topics:

            return 0.0, []

        filename = self._normalize_text(
            metadata.get(
                "filename",
                ""
            )
        )

        document_name = self._normalize_text(
            metadata.get(
                "document_name",
                ""
            )
        )

        metadata_text = (
            f"{filename} "
            f"{document_name}"
        )

        matched = []

        for topic in topics:

            keywords = (
                self.DOCUMENT_TOPIC_KEYWORDS.get(
                    topic,
                    []
                )
            )

            for keyword in keywords:

                if keyword in metadata_text:

                    matched.append(
                        topic
                    )

                    break

        score = (
            len(matched)
            / len(topics)
        )

        return score, matched

    # =====================================================
    # KEYWORD BOOST
    # =====================================================

    def _calculate_keyword_boost(
        self,
        question,
        metadata
    ):

        analysis = self._analyze_keywords(
            question,
            metadata
        )

        matched_keywords = list(
            dict.fromkeys(
                analysis["document_matches"]
                + analysis["filename_matches"]
                + analysis["text_matches"]
            )
        )

        return (
            analysis["boost"],
            matched_keywords
        )

    # =====================================================
    # DETECT VALUE QUESTION
    # =====================================================

    def _is_value_question(
        self,
        question
    ):

        question_text = self._normalize_text(
            question
        )

        return any(
            term in question_text
            for term in self.VALUE_TERMS
        )

    # =====================================================
    # HAS MONEY
    # =====================================================

    def _has_money(
        self,
        text
    ):

        text = self._normalize_text(
            text
        )

        money_patterns = [

            r"\bidr\s*[\d\.,]+",

            r"\brp\.?\s*[\d\.,]+",

            r"\b\d{1,3}(?:[\.,]\d{3})+(?:[\.,]\d+)?\b",
        ]

        return any(
            re.search(
                pattern,
                text,
                re.IGNORECASE
            )
            for pattern in money_patterns
        )

    # =====================================================
    # ANSWER EVIDENCE
    # =====================================================

    def _calculate_answer_evidence(
        self,
        question,
        metadata
    ):

        text = self._normalize_text(
            metadata.get(
                "text",
                ""
            )
        )

        score = 0.0
        matches = []

        # -------------------------------------------------
        # TABLE
        # -------------------------------------------------

        has_table = (
            "[table" in text
            or "<table" in text
            or "table 3" in text
            or "table 2" in text
            or "table 1" in text
        )

        if has_table:

            score += 0.20

            matches.append(
                "table"
            )

        # -------------------------------------------------
        # ANSWER TERMS
        # -------------------------------------------------

        answer_term_matches = [

            term

            for term in self.ANSWER_EVIDENCE_TERMS

            if term in text
        ]

        if answer_term_matches:

            score += 0.25

            matches.extend(
                answer_term_matches
            )

        # -------------------------------------------------
        # MONEY
        # -------------------------------------------------

        has_money = self._has_money(
            text
        )

        if has_money:

            score += 0.20

            matches.append(
                "currency"
            )

        # -------------------------------------------------
        # VALUE QUESTION
        # -------------------------------------------------

        value_question = self._is_value_question(
            question
        )

        if value_question:

            strong_matches = [

                term

                for term in self.STRONG_VALUE_TERMS

                if term in text
            ]

            if strong_matches:

                score += 0.25

                matches.append(
                    "limit-answer"
                )

            elif (
                "reimbursement" in text
                and has_money
            ):

                score += 0.10

                matches.append(
                    "reimbursement-with-money"
                )

            elif (
                "penggantian" in text
                and has_money
            ):

                score += 0.10

                matches.append(
                    "penggantian-with-money"
                )

        return {
            "score": min(
                score,
                1.0
            ),

            "matches": list(
                dict.fromkeys(
                    matches
                )
            )
        }

    # =====================================================
    # ANSWER EVIDENCE SCORE
    # =====================================================

    def _calculate_answer_evidence_score(
        self,
        text,
        question
    ):

        if not text or not question:

            return 0.0

        text_lower = self._normalize_text(
            text
        )

        question_lower = self._normalize_text(
            question
        )

        if not self._is_value_question(
            question_lower
        ):

            return 0.0

        score = 0.0

        # -------------------------------------------------
        # STRONG VALUE TERMS
        # -------------------------------------------------

        matched_strong_terms = [

            term

            for term in self.STRONG_VALUE_TERMS

            if term in text_lower
        ]

        if matched_strong_terms:

            score += 0.60

        else:

            # Generic reimbursement tidak boleh
            # dianggap strong answer.

            if (
                "reimbursement" in text_lower
                and (
                    "limit" in text_lower
                    or "maksimum" in text_lower
                    or "maksimal" in text_lower
                    or "penggantian" in text_lower
                )
            ):

                score += 0.40

            elif (
                "reimbursement" in text_lower
                and self._has_money(
                    text_lower
                )
            ):

                score += 0.20

            elif (
                "penggantian" in text_lower
                and self._has_money(
                    text_lower
                )
            ):

                score += 0.20

        # -------------------------------------------------
        # MONEY
        # -------------------------------------------------

        if self._has_money(
            text_lower
        ):

            score += 0.40

        # -------------------------------------------------
        # TABLE
        # -------------------------------------------------

        if (
            "[table" in text_lower
            or "<table" in text_lower
            or "table 3" in text_lower
        ):

            score += 0.10

        # -------------------------------------------------
        # KACAMATA CONTEXT
        #
        # PENTING:
        #
        # Jangan langsung mengurangi score di sini.
        #
        # Karena chunk tabel bisa tidak mengandung kata
        # kacamata tetapi tetap merupakan answer-bearing
        # chunk dari dokumen kacamata.
        #
        # Context guard dilakukan di level candidate.
        # -------------------------------------------------

        return max(
            0.0,
            min(
                score,
                1.0
            )
        )

    # =====================================================
    # CALCULATE FINAL SCORE
    # =====================================================

    def _calculate_final_score(
        self,
        raw_score,
        analysis,
        text="",
        question="",
        metadata=None
    ):

        # -------------------------------------------------
        # SEMANTIC
        # -------------------------------------------------

        semantic_score = max(
            0.0,
            min(
                float(raw_score),
                1.0
            )
        )

        # -------------------------------------------------
        # KEYWORD
        # -------------------------------------------------

        if self.MAX_KEYWORD_BOOST > 0:

            keyword_score = (
                analysis["boost"]
                / self.MAX_KEYWORD_BOOST
            )

        else:

            keyword_score = 0.0

        keyword_score = max(
            0.0,
            min(
                keyword_score,
                1.0
            )
        )

        # -------------------------------------------------
        # EVIDENCE
        # -------------------------------------------------

        important_component = (
            analysis[
                "important_coverage"
            ]
            * 0.60
        )

        coverage_component = (
            analysis[
                "coverage"
            ]
            * 0.25
        )

        phrase_component = (

            min(
                len(
                    analysis[
                        "phrase_matches"
                    ]
                ),
                2
            )

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
            min(
                evidence_score,
                1.0
            )
        )

        # -------------------------------------------------
        # ANSWER EVIDENCE
        # -------------------------------------------------

        answer_evidence_score = (
            self._calculate_answer_evidence_score(
                text,
                question
            )
        )

        # -------------------------------------------------
        # TOPIC CONTEXT
        # -------------------------------------------------

        topic_context_score, matched_topic_contexts = (
            self._calculate_topic_context_score(
                question,
                metadata or {}
            )
        )

        # -------------------------------------------------
        # KACAMATA CONTEXT
        # -------------------------------------------------

        kacamata_context_score, has_kacamata_context = (
            self._calculate_kacamata_context_score(
                question,
                metadata or {}
            )
        )

        # -------------------------------------------------
        # BASE SCORE
        #
        # EXACTLY:
        #
        # Semantic        50%
        # Keyword         20%
        # Evidence        15%
        # Answer Evidence 15%
        #
        # = 100%
        # -------------------------------------------------

        base_score = (

            semantic_score
            * self.SEMANTIC_WEIGHT

            + keyword_score
            * self.KEYWORD_WEIGHT

            + evidence_score
            * self.EVIDENCE_WEIGHT

            + answer_evidence_score
            * self.ANSWER_EVIDENCE_WEIGHT
        )

        # -------------------------------------------------
        # TOPIC CONTEXT ADJUSTMENT
        # -------------------------------------------------

        query_topics = (
            self._detect_query_topics(
                question
            )
        )

        if query_topics:

            if topic_context_score > 0:

                base_score += (
                    topic_context_score
                    * self.TOPIC_ANSWER_BOOST
                )

            else:

                base_score -= (
                    self.TOPIC_MISMATCH_PENALTY
                )

        # -------------------------------------------------
        # KACAMATA CONTEXT ADJUSTMENT
        # -------------------------------------------------

        if "kacamata" in query_topics:

            if has_kacamata_context:

                base_score += (
                    self.KACAMATA_CONTEXT_BOOST
                )

            else:

                # Jangan langsung membuang chunk.
                #
                # Chunk tabel dapat memperoleh context
                # dari neighbor nanti.
                #
                # Untuk primary yang belum punya context,
                # hanya penalty kecil.
                base_score -= (
                    self.KACAMATA_CONTEXT_PENALTY
                )

        # -------------------------------------------------
        # VALUE QUESTION TOPIC ADJUSTMENT
        # -------------------------------------------------

        if self._is_value_question(
            question
        ):

            topic_score, _ = (
                self._calculate_topic_score(
                    question,
                    text,
                    metadata
                )
            )

            if topic_score > 0:

                base_score += (
                    topic_score
                    * self.VALUE_QUESTION_BOOST
                )

        final_score = max(
            0.0,
            min(
                base_score,
                1.0
            )
        )

        return {

            "semantic_score":
                semantic_score,

            "keyword_score":
                keyword_score,

            "evidence_score":
                evidence_score,

            "answer_evidence_score":
                answer_evidence_score,

            "topic_context_score":
                topic_context_score,

            "matched_topic_contexts":
                matched_topic_contexts,

            "kacamata_context_score":
                kacamata_context_score,

            "has_kacamata_context":
                has_kacamata_context,

            "topic_score":
                0.0,

            "document_topic_score":
                0.0,

            "matched_topics":
                [],

            "final_score":
                final_score,
        }

    # =====================================================
    # FIND NEIGHBOR CHUNKS
    # =====================================================

    def _find_neighbor_chunks(
        self,
        metadata,
        distance=None
    ):

        if distance is None:

            distance = (
                self.NEIGHBOR_DISTANCE
            )

        document_key = (
            self._get_document_key(
                metadata
            )
        )

        chunk_id = (
            self._get_chunk_id(
                metadata
            )
        )

        neighbors = []

        for index, item in enumerate(
            self.metadata
        ):

            if item is metadata:

                continue

            other_document = (
                self._get_document_key(
                    item
                )
            )

            if (
                other_document
                != document_key
            ):

                continue

            other_chunk_id = (
                self._get_chunk_id(
                    item
                )
            )

            chunk_distance = abs(
                other_chunk_id
                - chunk_id
            )

            if (
                chunk_distance
                <= distance
            ):

                neighbors.append(
                    {
                        "metadata": item,
                        "index": index,
                        "distance":
                            chunk_distance,
                    }
                )

        return neighbors

    # =====================================================
    # CHECK KACAMATA NEIGHBOR CONTEXT
    # =====================================================

    def _find_kacamata_neighbor_context(
        self,
        metadata
    ):

        document_key = (
            self._get_document_key(
                metadata
            )
        )

        chunk_id = (
            self._get_chunk_id(
                metadata
            )
        )

        for item in self.metadata:

            if item is metadata:
                continue

            if (
                self._get_document_key(item)
                != document_key
            ):
                continue

            other_chunk_id = (
                self._get_chunk_id(item)
            )

            if abs(
                other_chunk_id - chunk_id
            ) > self.NEIGHBOR_DISTANCE:

                continue

            text = self._normalize_text(
                item.get(
                    "text",
                    ""
                )
            )

            filename = self._normalize_text(
                item.get(
                    "filename",
                    ""
                )
            )

            document_name = self._normalize_text(
                item.get(
                    "document_name",
                    ""
                )
            )

            searchable = (
                f"{text} "
                f"{filename} "
                f"{document_name}"
            )

            if any(
                term in searchable
                for term in self.KACAMATA_TERMS
            ):

                return True

        return False

    # =====================================================
    # APPLY INHERITED KACAMATA CONTEXT
    # =====================================================

    def _apply_kacamata_context_inheritance(
        self,
        candidate,
        question
    ):

        query_topics = (
            self._detect_query_topics(
                question
            )
        )

        if "kacamata" not in query_topics:

            return candidate

        if candidate.get(
            "has_kacamata_context",
            False
        ):

            return candidate

        metadata = candidate[
            "metadata"
        ]

        inherited = (
            self._find_kacamata_neighbor_context(
                metadata
            )
        )

        if inherited:

            candidate[
                "has_kacamata_context"
            ] = True

            candidate[
                "kacamata_context_score"
            ] = 1.0

            candidate[
                "inherited_kacamata_context"
            ] = True

            # Hanya boost kecil karena context berasal
            # dari neighbor, bukan chunk itu sendiri.

            candidate[
                "score"
            ] += self.INHERITED_TOPIC_BOOST

            candidate[
                "score"
            ] = max(
                0.0,
                min(
                    candidate["score"],
                    1.0
                )
            )

        else:

            candidate[
                "inherited_kacamata_context"
            ] = False

        return candidate

    # =====================================================
    # SEARCH
    # =====================================================

    def search(
        self,
        query_vector,
        question="",
        top_k=3
    ):

        print()
        print("=" * 80)
        print("VECTOR STORE SEARCH")
        print("=" * 80)

        print(
            "Question:",
            repr(question)
        )

        print(
            "Requested Top K:",
            top_k
        )

        # =================================================
        # EMPTY INDEX
        # =================================================

        if self.index.ntotal == 0:

            print(
                "Vector index kosong."
            )

            print("=" * 80)

            return []

        # =================================================
        # METADATA CHECK
        # =================================================

        if (
            len(self.metadata)
            != self.index.ntotal
        ):

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
        # CANDIDATE K
        # =================================================

        candidate_k = max(

            top_k
            * self.CANDIDATE_MULTIPLIER,

            self.MIN_CANDIDATE_K
        )

        candidate_k = min(
            candidate_k,
            self.index.ntotal
        )

        # =================================================
        # QUERY VECTOR
        # =================================================

        query = np.asarray(
            query_vector,
            dtype=np.float32
        )

        if query.ndim == 1:

            query = np.expand_dims(
                query,
                axis=0
            )

        if query.ndim != 2:

            raise ValueError(
                "Query vector harus berupa "
                "array 1D atau 2D."
            )

        if query.shape[1] != self.dimension:

            raise ValueError(
                "Dimensi query vector "
                "tidak sesuai. "
                f"Expected={self.dimension}, "
                f"Actual={query.shape[1]}"
            )

        # =================================================
        # NORMALIZE
        # =================================================

        faiss.normalize_L2(
            query
        )

        # =================================================
        # FAISS SEARCH
        # =================================================

        scores, indexes = (
            self.index.search(
                query,
                candidate_k
            )
        )

        print(
            "FAISS Candidate Count:",
            candidate_k
        )

        print(
            "Total Vector:",
            self.index.ntotal
        )

        # =================================================
        # ORIGINAL SEMANTIC SCORE MAP
        # =================================================

        semantic_scores_by_index = {}

        for raw_score, idx in zip(
            scores[0],
            indexes[0]
        ):

            if idx == -1:
                continue

            semantic_scores_by_index[
                int(idx)
            ] = float(
                raw_score
            )

        # =================================================
        # QUERY INFO
        # =================================================

        query_topics = (
            self._detect_query_topics(
                question
            )
        )

        value_question = (
            self._is_value_question(
                question
            )
        )

        keywords = self._tokenize(
            question
        )

        print(
            "Detected Topics:",
            query_topics
        )

        print(
            "Value Question:",
            value_question
        )

        print(
            "Keywords:",
            keywords
        )

        # =================================================
        # PRIMARY CANDIDATES
        # =================================================

        primary_candidates = []

        for raw_score, idx in zip(
            scores[0],
            indexes[0]
        ):

            if idx == -1:
                continue

            idx = int(idx)

            metadata = (
                self.metadata[idx]
            )

            raw_score = float(
                raw_score
            )

            # -------------------------------------------------
            # KEYWORD
            # -------------------------------------------------

            analysis = (
                self._analyze_keywords(
                    question,
                    metadata
                )
            )

            # -------------------------------------------------
            # FINAL SCORE
            # -------------------------------------------------

            score_data = (
                self._calculate_final_score(
                    raw_score,
                    analysis,
                    text=metadata.get(
                        "text",
                        ""
                    ),
                    question=question,
                    metadata=metadata
                )
            )

            # -------------------------------------------------
            # TOPIC
            # -------------------------------------------------

            topic_score, matched_topics = (
                self._calculate_topic_score(
                    question,
                    metadata.get(
                        "text",
                        ""
                    ),
                    metadata
                )
            )

            document_topic_score, matched_document_topics = (
                self._calculate_document_topic_score(
                    question,
                    metadata
                )
            )

            # -------------------------------------------------
            # TOPIC ADJUSTMENT
            # -------------------------------------------------

            topic_adjustment = 0.0

            if query_topics:

                if topic_score > 0:

                    topic_adjustment += (
                        topic_score
                        * self.TOPIC_BOOST
                    )

                if document_topic_score > 0:

                    topic_adjustment += (
                        document_topic_score
                        * self.DOCUMENT_TOPIC_BOOST
                    )

            final_score = (
                score_data["final_score"]
                + topic_adjustment
            )

            # -------------------------------------------------
            # BUILD CANDIDATE
            # -------------------------------------------------

            candidate = {

                "index":
                    idx,

                "metadata":
                    metadata,

                "raw_score":
                    raw_score,

                "semantic_score":
                    score_data[
                        "semantic_score"
                    ],

                "keyword_score":
                    score_data[
                        "keyword_score"
                    ],

                "evidence_score":
                    score_data[
                        "evidence_score"
                    ],

                "answer_evidence_score":
                    score_data[
                        "answer_evidence_score"
                    ],

                "topic_context_score":
                    score_data.get(
                        "topic_context_score",
                        0.0
                    ),

                "matched_topic_contexts":
                    score_data.get(
                        "matched_topic_contexts",
                        []
                    ),

                "kacamata_context_score":
                    score_data.get(
                        "kacamata_context_score",
                        0.0
                    ),

                "has_kacamata_context":
                    score_data.get(
                        "has_kacamata_context",
                        False
                    ),

                "inherited_kacamata_context":
                    False,

                "topic_score":
                    topic_score,

                "document_topic_score":
                    document_topic_score,

                "matched_topics":
                    matched_topics,

                "matched_document_topics":
                    matched_document_topics,

                "boost":
                    analysis[
                        "boost"
                    ],

                "analysis":
                    analysis,

                "score":
                    max(
                        0.0,
                        min(
                            final_score,
                            1.0
                        )
                    ),

                "primary":
                    True,

                "neighbor":
                    False,

                "distance":
                    0,
            }

            # -------------------------------------------------
            # KACAMATA CONTEXT INHERITANCE
            #
            # Penting untuk chunk tabel yang tidak menyebut
            # kata "kacamata" tetapi bersebelahan dengan chunk
            # heading/topik kacamata.
            # -------------------------------------------------

            candidate = (
                self._apply_kacamata_context_inheritance(
                    candidate,
                    question
                )
            )

            primary_candidates.append(
                candidate
            )

        # =================================================
        # SORT PRIMARY
        # =================================================

        primary_candidates.sort(

            key=lambda item: (

                item["score"],

                item["raw_score"],

                item[
                    "document_topic_score"
                ],

                item[
                    "topic_score"
                ],

                item[
                    "answer_evidence_score"
                ],

                item[
                    "kacamata_context_score"
                ],

                item[
                    "analysis"
                ][
                    "important_coverage"
                ],

                item[
                    "analysis"
                ][
                    "coverage"
                ],

            ),

            reverse=True,
        )

        # =================================================
        # SEED
        # =================================================

        seed_count = min(

            max(
                top_k * 3,
                6
            ),

            len(
                primary_candidates
            )
        )

        seed_candidates = (
            primary_candidates[
                :seed_count
            ]
        )

        context_candidates = []

        seen_indexes = set()

        # =================================================
        # ADD PRIMARY SEEDS
        # =================================================

        for item in seed_candidates:

            index = item["index"]

            if index in seen_indexes:
                continue

            seen_indexes.add(
                index
            )

            context_candidates.append(
                item
            )

        # =================================================
        # ADD NEIGHBORS
        # =================================================

        for primary in seed_candidates:

            neighbors = (
                self._find_neighbor_chunks(
                    primary["metadata"]
                )
            )

            for neighbor in neighbors:

                neighbor_index = (
                    neighbor["index"]
                )

                if neighbor_index in seen_indexes:

                    continue

                neighbor_metadata = (
                    neighbor["metadata"]
                )

                analysis = (
                    self._analyze_keywords(
                        question,
                        neighbor_metadata
                    )
                )

                distance = (
                    neighbor["distance"]
                )

                # -------------------------------------------------
                # TOPIC
                # -------------------------------------------------

                topic_score, matched_topics = (
                    self._calculate_topic_score(
                        question,
                        neighbor_metadata.get(
                            "text",
                            ""
                        ),
                        neighbor_metadata
                    )
                )

                document_topic_score, matched_document_topics = (
                    self._calculate_document_topic_score(
                        question,
                        neighbor_metadata
                    )
                )

                # -------------------------------------------------
                # ANSWER EVIDENCE
                # -------------------------------------------------

                neighbor_answer_evidence = (
                    self._calculate_answer_evidence_score(
                        neighbor_metadata.get(
                            "text",
                            ""
                        ),
                        question
                    )
                )

                # -------------------------------------------------
                # KACAMATA CONTEXT DIRECT
                # -------------------------------------------------

                (
                    kacamata_context_score,
                    has_kacamata_context
                ) = (
                    self._calculate_kacamata_context_score(
                        question,
                        neighbor_metadata
                    )
                )

                # -------------------------------------------------
                # KACAMATA CONTEXT INHERITED
                # -------------------------------------------------

                inherited_kacamata_context = False

                if (
                    "kacamata" in query_topics
                    and not has_kacamata_context
                ):

                    inherited_kacamata_context = (
                        self._find_kacamata_neighbor_context(
                            neighbor_metadata
                        )
                    )

                    if inherited_kacamata_context:

                        has_kacamata_context = True

                        kacamata_context_score = 1.0

                # -------------------------------------------------
                # RELEVANCE
                # -------------------------------------------------

                has_topic = (
                    topic_score > 0
                    or document_topic_score > 0
                )

                has_keyword = (
                    analysis[
                        "important_coverage"
                    ] > 0.0

                    or bool(
                        analysis[
                            "phrase_matches"
                        ]
                    )
                )

                has_answer_evidence = (
                    neighbor_answer_evidence
                    > 0.0
                )

                # Untuk value question, table + money
                # merupakan evidence penting walaupun keyword
                # question tidak muncul secara literal.

                has_value_evidence = (

                    value_question

                    and (
                        self._has_money(
                            neighbor_metadata.get(
                                "text",
                                ""
                            )
                        )

                        or "[table" in self._normalize_text(
                            neighbor_metadata.get(
                                "text",
                                ""
                            )
                        )
                    )
                )

                if not (
                    has_topic
                    or has_keyword
                    or has_answer_evidence
                    or has_value_evidence
                ):

                    print(
                        ">>> SKIP NEIGHBOR - "
                        "tidak relevan"
                    )

                    continue

                # -------------------------------------------------
                # ORIGINAL SEMANTIC SCORE
                # -------------------------------------------------

                if neighbor_index in semantic_scores_by_index:

                    neighbor_raw_score = (
                        semantic_scores_by_index[
                            neighbor_index
                        ]
                    )

                else:

                    neighbor_raw_score = (
                        primary[
                            "raw_score"
                        ]
                        - 0.10
                    )

                    neighbor_raw_score = max(
                        0.0,
                        neighbor_raw_score
                    )

                # -------------------------------------------------
                # BASE SCORE
                # -------------------------------------------------

                score_data = (
                    self._calculate_final_score(
                        neighbor_raw_score,
                        analysis,
                        text=neighbor_metadata.get(
                            "text",
                            ""
                        ),
                        question=question,
                        metadata=neighbor_metadata
                    )
                )

                # -------------------------------------------------
                # TOPIC ADJUSTMENT
                # -------------------------------------------------

                topic_adjustment = 0.0

                if query_topics:

                    topic_adjustment += (
                        topic_score
                        * self.TOPIC_BOOST
                    )

                    topic_adjustment += (
                        document_topic_score
                        * self.DOCUMENT_TOPIC_BOOST
                    )

                final_score = (
                    score_data[
                        "final_score"
                    ]
                    + topic_adjustment
                )

                # -------------------------------------------------
                # KACAMATA CONTEXT
                # -------------------------------------------------

                if "kacamata" in query_topics:

                    if has_kacamata_context:

                        final_score += (
                            self.KACAMATA_CONTEXT_BOOST
                        )

                    else:

                        # Hanya penalty untuk chunk yang benar-benar
                        # tidak punya context.
                        final_score -= (
                            self.KACAMATA_CONTEXT_PENALTY
                        )

                # -------------------------------------------------
                # VALUE QUESTION GUARD
                # -------------------------------------------------

                if value_question:

                    if query_topics:

                        if topic_score == 0:

                            # Jika tidak punya topic langsung tetapi
                            # punya context kacamata dari neighbor,
                            # JANGAN menghukum.

                            if (
                                "kacamata" in query_topics
                                and has_kacamata_context
                            ):

                                pass

                            elif (
                                neighbor_answer_evidence
                                < 0.60
                            ):

                                final_score -= 0.05

                # -------------------------------------------------
                # INHERITED CONTEXT BOOST
                # -------------------------------------------------

                if inherited_kacamata_context:

                    final_score += (
                        self.INHERITED_TOPIC_BOOST
                    )

                # -------------------------------------------------
                # NEIGHBOR PENALTY
                # -------------------------------------------------

                neighbor_penalty = (
                    self.NEIGHBOR_SCORE_PENALTY
                    * distance
                )

                final_score -= (
                    neighbor_penalty
                )

                final_score = max(
                    0.0,
                    min(
                        final_score,
                        1.0
                    )
                )

                context_candidates.append(
                    {

                        "index":
                            neighbor_index,

                        "metadata":
                            neighbor_metadata,

                        "raw_score":
                            float(
                                neighbor_raw_score
                            ),

                        "semantic_score":
                            score_data[
                                "semantic_score"
                            ],

                        "keyword_score":
                            score_data[
                                "keyword_score"
                            ],

                        "evidence_score":
                            score_data[
                                "evidence_score"
                            ],

                        "answer_evidence_score":
                            score_data[
                                "answer_evidence_score"
                            ],

                        "topic_context_score":
                            score_data.get(
                                "topic_context_score",
                                0.0
                            ),

                        "kacamata_context_score":
                            kacamata_context_score,

                        "has_kacamata_context":
                            has_kacamata_context,

                        "inherited_kacamata_context":
                            inherited_kacamata_context,

                        "topic_score":
                            topic_score,

                        "document_topic_score":
                            document_topic_score,

                        "matched_topics":
                            matched_topics,

                        "matched_document_topics":
                            matched_document_topics,

                        "boost":
                            analysis[
                                "boost"
                            ],

                        "analysis":
                            analysis,

                        "score":
                            float(
                                final_score
                            ),

                        "primary":
                            False,

                        "neighbor":
                            True,

                        "distance":
                            distance,
                    }
                )

        # =================================================
        # ADD REMAINING PRIMARY
        # =================================================

        for item in primary_candidates:

            index = item["index"]

            if index in seen_indexes:
                continue

            analysis = item["analysis"]

            topic_match = (
                item[
                    "topic_score"
                ] > 0

                or item[
                    "document_topic_score"
                ] > 0
            )

            answer_match = (
                item[
                    "answer_evidence_score"
                ] > 0
            )

            value_match = (
                value_question
                and (
                    self._has_money(
                        item[
                            "metadata"
                        ].get(
                            "text",
                            ""
                        )
                    )
                    or "[table" in self._normalize_text(
                        item[
                            "metadata"
                        ].get(
                            "text",
                            ""
                        )
                    )
                )
            )

            if (

                analysis[
                    "important_coverage"
                ] > 0.0

                or analysis[
                    "coverage"
                ] >= 0.50

                or topic_match

                or answer_match

                or value_match
            ):

                context_candidates.append(
                    item
                )

                seen_indexes.add(
                    index
                )

        # =================================================
        # DEDUPLICATE
        # =================================================

        unique_candidates = {}

        for item in context_candidates:

            index = item["index"]

            current = (
                unique_candidates.get(
                    index
                )
            )

            if current is None:

                unique_candidates[
                    index
                ] = item

                continue

            if (
                item["primary"]
                and not current["primary"]
            ):

                unique_candidates[
                    index
                ] = item

                continue

            if (
                item["score"]
                > current["score"]
            ):

                unique_candidates[
                    index
                ] = item

        context_candidates = list(
            unique_candidates.values()
        )

        # =================================================
        # SORT CONTEXT
        # =================================================

        context_candidates.sort(

            key=lambda item: (

                item["score"],

                item["raw_score"],

                item[
                    "document_topic_score"
                ],

                item[
                    "topic_score"
                ],

                item[
                    "answer_evidence_score"
                ],

                item[
                    "kacamata_context_score"
                ],

                item[
                    "analysis"
                ][
                    "important_coverage"
                ],

                item[
                    "analysis"
                ][
                    "coverage"
                ],

                len(
                    item[
                        "analysis"
                    ][
                        "phrase_matches"
                    ]
                ),

                1 if item[
                    "primary"
                ] else 0,

                -item[
                    "distance"
                ],
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

        for rank, item in enumerate(
            context_candidates,
            start=1
        ):

            metadata = (
                item["metadata"]
            )

            analysis = (
                item["analysis"]
            )

            print()
            print(
                f"Context #{rank}"
            )

            print(
                "-" * 60
            )

            print(
                "Document:",
                metadata.get(
                    "document_name",
                    ""
                )
            )

            print(
                "Chunk:",
                metadata.get(
                    "chunk_id",
                    0
                )
            )

            print(
                "Raw / Semantic:",
                round(
                    item[
                        "raw_score"
                    ],
                    4
                )
            )

            print(
                "Semantic Score:",
                round(
                    item[
                        "semantic_score"
                    ],
                    4
                )
            )

            print(
                "Keyword Score:",
                round(
                    item[
                        "keyword_score"
                    ],
                    4
                )
            )

            print(
                "Evidence Score:",
                round(
                    item[
                        "evidence_score"
                    ],
                    4
                )
            )

            print(
                "Answer Evidence:",
                round(
                    item[
                        "answer_evidence_score"
                    ],
                    4
                )
            )

            print(
                "Topic Context:",
                round(
                    item.get(
                        "topic_context_score",
                        0.0
                    ),
                    4
                )
            )

            print(
                "Kacamata Context:",
                round(
                    item.get(
                        "kacamata_context_score",
                        0.0
                    ),
                    4
                )
            )

            print(
                "Has Kacamata Context:",
                item.get(
                    "has_kacamata_context",
                    False
                )
            )

            print(
                "Inherited Kacamata:",
                item.get(
                    "inherited_kacamata_context",
                    False
                )
            )

            print(
                "Topic Score:",
                round(
                    item[
                        "topic_score"
                    ],
                    4
                )
            )

            print(
                "Document Topic:",
                round(
                    item[
                        "document_topic_score"
                    ],
                    4
                )
            )

            print(
                "Matched Topics:",
                item.get(
                    "matched_topics",
                    []
                )
            )

            print(
                "Final Score:",
                round(
                    item[
                        "score"
                    ],
                    4
                )
            )

            print(
                "Keyword Boost:",
                round(
                    item[
                        "boost"
                    ],
                    4
                )
            )

            print(
                "Coverage:",
                round(
                    analysis[
                        "coverage"
                    ],
                    4
                )
            )

            print(
                "Important Coverage:",
                round(
                    analysis[
                        "important_coverage"
                    ],
                    4
                )
            )

            print(
                "Phrase Matches:",
                analysis[
                    "phrase_matches"
                ]
            )

            print(
                "Primary:",
                item[
                    "primary"
                ]
            )

            print(
                "Neighbor:",
                item[
                    "neighbor"
                ]
            )

            print(
                "Distance:",
                item[
                    "distance"
                ]
            )

            print(
                "Preview:",
                metadata.get(
                    "text",
                    ""
                )[:500]
            )

        # =================================================
        # NO CANDIDATE
        # =================================================

        if not context_candidates:

            print(
                "Tidak ada candidate."
            )

            print("=" * 80)

            return []

        # =================================================
        # BEST SCORE
        # =================================================

        best_score = (
            context_candidates[0][
                "score"
            ]
        )

        # =================================================
        # RELATIVE THRESHOLD
        # =================================================

        relative_threshold = (
            best_score
            - self.RELATIVE_SCORE_MARGIN
        )

        threshold = max(
            self.MIN_SIMILARITY_SCORE,
            relative_threshold
        )

        print()

        print(
            f"Best Score         : "
            f"{best_score:.4f}"
        )

        print(
            f"Minimum Score      : "
            f"{self.MIN_SIMILARITY_SCORE:.4f}"
        )

        print(
            f"Relative Threshold : "
            f"{relative_threshold:.4f}"
        )

        print(
            f"Final Threshold    : "
            f"{threshold:.4f}"
        )

        print("=" * 80)

        # =================================================
        # FILTER
        # =================================================

        results = []

        for rank, item in enumerate(
            context_candidates,
            start=1
        ):

            metadata = (
                item["metadata"]
            )

            score = (
                item["score"]
            )

            raw_score = (
                item["raw_score"]
            )

            boost = (
                item["boost"]
            )

            analysis = (
                item["analysis"]
            )

            matched_keywords = list(
                dict.fromkeys(

                    analysis[
                        "document_matches"
                    ]

                    + analysis[
                        "filename_matches"
                    ]

                    + analysis[
                        "text_matches"
                    ]
                )
            )

            print()

            print(
                f"Context Candidate #{rank}"
            )

            print(
                "Document:",
                metadata.get(
                    "document_name",
                    ""
                )
            )

            print(
                "Chunk:",
                metadata.get(
                    "chunk_id",
                    0
                )
            )

            print(
                "Final:",
                round(
                    score,
                    4
                )
            )

            print(
                "Semantic:",
                round(
                    item[
                        "semantic_score"
                    ],
                    4
                )
            )

            print(
                "Keyword:",
                round(
                    item[
                        "keyword_score"
                    ],
                    4
                )
            )

            print(
                "Evidence:",
                round(
                    item[
                        "evidence_score"
                    ],
                    4
                )
            )

            print(
                "Answer Evidence:",
                round(
                    item[
                        "answer_evidence_score"
                    ],
                    4
                )
            )

            print(
                "Kacamata Context:",
                round(
                    item.get(
                        "kacamata_context_score",
                        0.0
                    ),
                    4
                )
            )

            print(
                "Has Kacamata Context:",
                item.get(
                    "has_kacamata_context",
                    False
                )
            )

            print(
                "Inherited Kacamata:",
                item.get(
                    "inherited_kacamata_context",
                    False
                )
            )

            print(
                "Topic Score:",
                round(
                    item[
                        "topic_score"
                    ],
                    4
                )
            )

            print(
                "Document Topic:",
                round(
                    item[
                        "document_topic_score"
                    ],
                    4
                )
            )

            print(
                "Coverage:",
                round(
                    analysis[
                        "coverage"
                    ],
                    4
                )
            )

            print(
                "Important Coverage:",
                round(
                    analysis[
                        "important_coverage"
                    ],
                    4
                )
            )

            print(
                "Keywords:",
                matched_keywords
            )

            print(
                "Phrase Matches:",
                analysis[
                    "phrase_matches"
                ]
            )

            print(
                "Primary:",
                item[
                    "primary"
                ]
            )

            print(
                "Neighbor:",
                item[
                    "neighbor"
                ]
            )

            print(
                "Distance:",
                item[
                    "distance"
                ]
            )

            print(
                "Preview:",
                metadata.get(
                    "text",
                    ""
                )[:500]
            )

            # =================================================
            # SCORE FILTER
            # =================================================

            if score < threshold:

                strong_evidence = (

                    analysis[
                        "important_coverage"
                    ] >= 0.75

                    or analysis[
                        "coverage"
                    ] >= 0.75

                    or len(
                        analysis[
                            "phrase_matches"
                        ]
                    ) >= 2

                    or item[
                        "answer_evidence_score"
                    ] >= 0.60

                    or item[
                        "document_topic_score"
                    ] >= 1.0

                    or (
                        item[
                            "topic_score"
                        ] >= 1.0

                        and item[
                            "answer_evidence_score"
                        ] >= 0.40
                    )
                )

                # -------------------------------------------------
                # VALUE + KACAMATA GUARD
                #
                # IMPORTANT:
                #
                # Jika candidate adalah answer-bearing chunk
                # yang memiliki context kacamata langsung ATAU
                # inherited, tetap boleh dianggap strong evidence.
                # -------------------------------------------------

                if (
                    value_question
                    and "kacamata" in query_topics
                ):

                    has_kacamata_context = (
                        item.get(
                            "has_kacamata_context",
                            False
                        )
                    )

                    answer_evidence = (
                        item[
                            "answer_evidence_score"
                        ]
                    )

                    has_money = (
                        self._has_money(
                            metadata.get(
                                "text",
                                ""
                            )
                        )
                    )

                    has_table = (
                        "[table" in self._normalize_text(
                            metadata.get(
                                "text",
                                ""
                            )
                        )
                        or "table 3" in self._normalize_text(
                            metadata.get(
                                "text",
                                ""
                            )
                        )
                    )

                    # -------------------------------------------------
                    # Strong kacamata answer:
                    #
                    # context + money/table
                    # -------------------------------------------------

                    if (
                        has_kacamata_context
                        and (
                            answer_evidence >= 0.40
                            or has_money
                            or has_table
                        )
                    ):

                        strong_evidence = True

                    # -------------------------------------------------
                    # Generic chunk tanpa context:
                    #
                    # jangan dianggap strong hanya karena money.
                    # -------------------------------------------------

                    elif (
                        not has_kacamata_context
                        and answer_evidence < 0.60
                    ):

                        strong_evidence = False

                if not strong_evidence:

                    print(
                        ">>> SKIP - "
                        "score terlalu rendah"
                    )

                    continue

                print(
                    ">>> KEEP - "
                    "strong evidence"
                )

            # =================================================
            # BUILD RESULT
            # =================================================

            result = metadata.copy()

            result["score"] = round(
                score,
                4
            )

            result["raw_score"] = round(
                raw_score,
                4
            )

            result["semantic_score"] = round(
                item[
                    "semantic_score"
                ],
                4
            )

            result["keyword_score"] = round(
                item[
                    "keyword_score"
                ],
                4
            )

            result["evidence_score"] = round(
                item[
                    "evidence_score"
                ],
                4
            )

            result[
                "answer_evidence_score"
            ] = round(
                item[
                    "answer_evidence_score"
                ],
                4
            )

            result[
                "topic_context_score"
            ] = round(
                item.get(
                    "topic_context_score",
                    0.0
                ),
                4
            )

            result[
                "kacamata_context_score"
            ] = round(
                item.get(
                    "kacamata_context_score",
                    0.0
                ),
                4
            )

            result[
                "has_kacamata_context"
            ] = item.get(
                "has_kacamata_context",
                False
            )

            result[
                "inherited_kacamata_context"
            ] = item.get(
                "inherited_kacamata_context",
                False
            )

            result[
                "topic_score"
            ] = round(
                item[
                    "topic_score"
                ],
                4
            )

            result[
                "document_topic_score"
            ] = round(
                item[
                    "document_topic_score"
                ],
                4
            )

            result[
                "keyword_boost"
            ] = round(
                boost,
                4
            )

            result[
                "matched_keywords"
            ] = matched_keywords

            result[
                "phrase_matches"
            ] = analysis[
                "phrase_matches"
            ]

            result[
                "keyword_coverage"
            ] = round(
                analysis[
                    "coverage"
                ],
                4
            )

            result[
                "important_keyword_coverage"
            ] = round(
                analysis[
                    "important_coverage"
                ],
                4
            )

            result[
                "matched_topics"
            ] = item.get(
                "matched_topics",
                []
            )

            result[
                "matched_document_topics"
            ] = item.get(
                "matched_document_topics",
                []
            )

            result[
                "neighbor"
            ] = item[
                "neighbor"
            ]

            result[
                "neighbor_distance"
            ] = item[
                "distance"
            ]

            results.append(
                result
            )

        # =================================================
        # FINAL RANKING
        # =================================================

        results.sort(

            key=lambda result: (

                result[
                    "score"
                ],

                result[
                    "raw_score"
                ],

                result[
                    "document_topic_score"
                ],

                result[
                    "topic_score"
                ],

                result[
                    "answer_evidence_score"
                ],

                result[
                    "kacamata_context_score"
                ],

                result[
                    "important_keyword_coverage"
                ],

                result[
                    "keyword_coverage"
                ],

                len(
                    result[
                        "phrase_matches"
                    ]
                ),

            ),

            reverse=True,
        )

        # =================================================
        # LIMIT TOP K
        # =================================================

        results = results[
            :top_k
        ]

        # =================================================
        # RESULT SUMMARY
        # =================================================

        print()

        print("=" * 80)
        print("FINAL SEARCH RESULT")
        print("=" * 80)

        print(
            "Result Count:",
            len(results)
        )

        for i, result in enumerate(
            results,
            start=1
        ):

            print()

            print(
                f"{i}. "
                f"{result.get('document_name', '')}"
                f" / "
                f"{result.get('chunk_id', 0)}"
            )

            print(
                "   Semantic Score : "
                f"{result['semantic_score']}"
            )

            print(
                "   Keyword Score  : "
                f"{result['keyword_score']}"
            )

            print(
                "   Evidence Score : "
                f"{result['evidence_score']}"
            )

            print(
                "   Answer Evidence: "
                f"{result['answer_evidence_score']}"
            )

            print(
                "   Topic Context  : "
                f"{result.get('topic_context_score', 0.0)}"
            )

            print(
                "   Kacamata Ctx.  : "
                f"{result.get('kacamata_context_score', 0.0)}"
                f" / "
                f"{result.get('has_kacamata_context', False)}"
            )

            print(
                "   Inherited Ctx. : "
                f"{result.get('inherited_kacamata_context', False)}"
            )

            print(
                "   Topic Score    : "
                f"{result['topic_score']}"
            )

            print(
                "   Document Topic : "
                f"{result['document_topic_score']}"
            )

            print(
                "   Final Score    : "
                f"{result['score']}"
            )

            print(
                "   Keyword Boost  : "
                f"{result['keyword_boost']}"
            )

            print(
                "   Coverage       : "
                f"{result['keyword_coverage']}"
            )

            print(
                "   Important Cov. : "
                f"{result['important_keyword_coverage']}"
            )

            print(
                "   Neighbor       : "
                f"{result['neighbor']}"
            )

            print(
                "   Neighbor Dist. : "
                f"{result['neighbor_distance']}"
            )

            print(
                "   Matched Topics : "
                f"{result.get('matched_topics', [])}"
            )

        print("=" * 80)

        return results

    # =====================================================
    # SAVE
    # =====================================================

    def save(self):

        VECTOR_INDEX.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        VECTOR_METADATA.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # -------------------------------------------------
        # Validate
        # -------------------------------------------------

        if (
            self.index.ntotal
            != len(self.metadata)
        ):

            raise RuntimeError(
                "Tidak dapat save VectorStore. "
                "Jumlah vector dan metadata tidak sama."
            )

        # -------------------------------------------------
        # Save FAISS
        # -------------------------------------------------

        faiss.write_index(
            self.index,
            str(VECTOR_INDEX)
        )

        # -------------------------------------------------
        # Save metadata
        # -------------------------------------------------

        joblib.dump(
            self.metadata,
            VECTOR_METADATA
        )

        print()

        print("=" * 60)
        print("VECTOR STORE SAVED")
        print("=" * 60)

        print(
            "Index    :",
            VECTOR_INDEX
        )

        print(
            "Metadata :",
            VECTOR_METADATA
        )

        print(
            "Vectors  :",
            self.index.ntotal
        )

        print(
            "Metadata :",
            len(self.metadata)
        )

        print("=" * 60)

    # =====================================================
    # LOAD
    # =====================================================

    def load(self):

        print()

        print("=" * 60)
        print("VECTOR STORE LOAD")
        print("=" * 60)

        print(
            "VECTOR_INDEX    :",
            VECTOR_INDEX
        )

        print(
            "VECTOR_METADATA :",
            VECTOR_METADATA
        )

        print(
            "INDEX EXISTS    :",
            VECTOR_INDEX.exists()
        )

        print(
            "META EXISTS     :",
            VECTOR_METADATA.exists()
        )

        print("=" * 60)

        # -------------------------------------------------
        # File check
        # -------------------------------------------------

        if not VECTOR_INDEX.exists():

            print(
                "Index tidak ditemukan."
            )

            return False

        if not VECTOR_METADATA.exists():

            print(
                "Metadata tidak ditemukan."
            )

            return False

        # -------------------------------------------------
        # Load index
        # -------------------------------------------------

        try:

            loaded_index = faiss.read_index(
                str(VECTOR_INDEX)
            )

        except Exception as e:

            print(
                "Gagal membaca FAISS index:"
            )

            print(
                repr(e)
            )

            return False

        # -------------------------------------------------
        # Dimension check
        # -------------------------------------------------

        if (
            loaded_index.d
            != self.dimension
        ):

            raise RuntimeError(

                "Dimensi FAISS index "
                "tidak sesuai. "

                f"Expected={self.dimension}, "

                f"Actual={loaded_index.d}"
            )

        # -------------------------------------------------
        # Load metadata
        # -------------------------------------------------

        try:

            metadata = joblib.load(
                VECTOR_METADATA
            )

        except Exception as e:

            print(
                "Gagal membaca metadata:"
            )

            print(
                repr(e)
            )

            return False

        # -------------------------------------------------
        # Validate metadata
        # -------------------------------------------------

        if not isinstance(
            metadata,
            list
        ):

            raise RuntimeError(
                "Format metadata tidak valid."
            )

        # -------------------------------------------------
        # Validate vector / metadata
        # -------------------------------------------------

        if (
            loaded_index.ntotal
            != len(metadata)
        ):

            raise RuntimeError(

                "Vector dan metadata "
                "tidak sinkron. "

                f"Vector={loaded_index.ntotal}, "

                f"Metadata={len(metadata)}"
            )

        # -------------------------------------------------
        # Apply
        # -------------------------------------------------

        self.index = loaded_index

        self.metadata = metadata

        print(
            "Vector index berhasil dimuat."
        )

        print(
            "Dimension      :",
            self.index.d
        )

        print(
            "Total Vector   :",
            self.index.ntotal
        )

        print(
            "Total Metadata :",
            len(self.metadata)
        )

        print("=" * 60)

        return True

    # =====================================================
    # EMPTY
    # =====================================================

    def is_empty(self):

        return (
            self.index.ntotal == 0
        )