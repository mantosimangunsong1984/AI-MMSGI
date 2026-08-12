import joblib
import faiss
import numpy as np
import re

from backend.utils.config import (
    VECTOR_INDEX,
    VECTOR_METADATA
)


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

    # -----------------------------------------------------
    # Important keywords
    #
    # Keyword yang sangat menentukan intent.
    # -----------------------------------------------------
    IMPORTANT_KEYWORDS = {

    # ==========================
    # HR POLICY
    # ==========================

    "cuti",
    "leave",
    "izin",
    "absensi",
    "kehadiran",
    "attendance",
    "probation",
    "masa",
    "percobaan",
    "resign",
    "resignation",
    "pengunduran",
    "termination",
    "phk",

    # ==========================
    # COMPENSATION
    # ==========================

    "gaji",
    "salary",
    "upah",
    "tunjangan",
    "allowance",
    "benefit",
    "bonus",
    "insentif",

    # ==========================
    # OVERTIME
    # ==========================

    "lembur",
    "overtime",
    "jam",
    "kerja",

    # ==========================
    # HEALTH BENEFIT
    # ==========================

    "bpjs",
    "kesehatan",
    "medical",
    "reimbursement",
    "claim",
    "klaim",
    "penggantian",
    "plafon",
    "limit",

    # ==========================
    # POLICY DOCUMENT
    # ==========================

    "policy",
    "kebijakan",
    "procedure",
    "prosedur",
    "sop",
    "aturan",
    "peraturan"

    }
    
    # -----------------------------------------------------
    # Generic keywords
    #
    # Keyword terlalu umum tidak boleh memberi
    # boost besar.
    # -----------------------------------------------------

    GENERIC_KEYWORDS = {

    "apa",
    "berapa",
    "bagaimana",
    "kapan",
    "siapa",
    "informasi",
    "terkait",
    "mengenai",
    "hal",
    "bagian"

    }

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

        "tersebut"

    }

    # =====================================================
    # INIT
    # =====================================================

    def __init__(
        self,
        dimension=DEFAULT_DIMENSION
    ):

        self.dimension = dimension

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.metadata = []

    # =====================================================
    # ADD VECTOR
    # =====================================================

    def add(
        self,
        embeddings
    ):

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

            # =============================================
            # VALIDATE DIMENSION
            # =============================================

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

            # =============================================
            # METADATA
            # =============================================

            self.metadata.append({

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
                )

            })

        vectors = np.asarray(
            vectors,
            dtype=np.float32
        )

        # =============================================
        # NORMALIZE VECTOR
        #
        # IndexFlatIP akan berfungsi sebagai cosine
        # similarity jika vector sudah normalized.
        # =============================================

        faiss.normalize_L2(
            vectors
        )

        # =============================================
        # ADD TO FAISS
        # =============================================

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
    # TOKENIZE QUESTION
    # =====================================================

    def _tokenize(
        self,
        text
    ):

        if not text:

            return []

        text = str(
            text
        ).lower()

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

        # Remove duplicate
        return list(
            dict.fromkeys(
                keywords
            )
        )

    # =====================================================
    # NORMALIZE TEXT
    # =====================================================

    def _normalize_text(
        self,
        text
    ):

        if not text:

            return ""

        text = str(
            text
        ).lower()

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # =====================================================
    # GET CHUNK ID
    # =====================================================

    def _get_chunk_id(
        self,
        metadata
    ):

        value = metadata.get(
            "chunk_id",
            0
        )

        try:

            return int(
                value
            )

        except Exception:

            return 0

    # =====================================================
    # GET DOCUMENT KEY
    # =====================================================

    def _get_document_key(
        self,
        metadata
    ):

        return (
            str(
                metadata.get(
                    "document_name",
                    ""
                )
            )
            .strip()
            .lower()
        )

    # =====================================================
    # PHRASE DETECTION
    # =====================================================

    def _build_phrases(
        self,
        keywords
    ):

        phrases = []

        if len(keywords) < 2:

            return phrases

        # =================================================
        # BIGRAM
        #
        # Phrase hanya berasal dari keyword pertanyaan.
        # =================================================

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

        # =================================================
        # SPECIFIC SEMANTIC PHRASES
        #
        # Hanya ditambahkan jika phrase tersebut memang
        # terdapat di pertanyaan.
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

            "klaim kacamata"

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

                "boost": 0.0

            }

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

        # =================================================
        # CLASSIFY KEYWORDS
        # =================================================

        for word in keywords:

            if word in self.IMPORTANT_KEYWORDS:

                important.append(
                    word
                )

            elif word in self.GENERIC_KEYWORDS:

                generic.append(
                    word
                )

        # =================================================
        # MATCH DOCUMENT
        # =================================================

        for word in keywords:

            if word in document_name:

                document_matches.append(
                    word
                )

        # =================================================
        # MATCH FILENAME
        # =================================================

        for word in keywords:

            if word in filename:

                filename_matches.append(
                    word
                )

        # =================================================
        # MATCH TEXT
        # =================================================

        for word in keywords:

            if word in text:

                text_matches.append(
                    word
                )

        # =================================================
        # PHRASE MATCH
        # =================================================

        phrases = self._build_phrases(
            keywords
        )

        phrase_matches = []

        for phrase in phrases:

            if phrase in text:

                phrase_matches.append(
                    phrase
                )

        # =================================================
        # COVERAGE
        #
        # Jangan menghitung duplicate match.
        # =================================================

        matched_keywords = list(
            dict.fromkeys(

                document_matches

                +

                filename_matches

                +

                text_matches

            )
        )

        coverage = (

            len(
                matched_keywords
            )

            /

            len(
                keywords
            )

        )

        # =================================================
        # IMPORTANT COVERAGE
        # =================================================

        if important:

            important_matched = [

                word

                for word in important

                if (

                    word in document_matches

                    or

                    word in filename_matches

                    or

                    word in text_matches

                )

            ]

            important_coverage = (

                len(
                    important_matched
                )

                /

                len(
                    important
                )

            )

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

            boost += (

                important_coverage

                *

                0.22

            )

        # -------------------------------------------------
        # TEXT COVERAGE
        # -------------------------------------------------

        boost += (

            coverage

            *

            0.08

        )

        # -------------------------------------------------
        # DOCUMENT NAME
        # -------------------------------------------------

        document_important_matches = [

            word

            for word in important

            if word in document_matches

        ]

        boost += min(

            len(
                document_important_matches
            )

            *

            0.08,

            0.16

        )

        # -------------------------------------------------
        # FILENAME
        # -------------------------------------------------

        filename_important_matches = [

            word

            for word in important

            if word in filename_matches

        ]

        boost += min(

            len(
                filename_important_matches
            )

            *

            0.05,

            0.10

        )

        # -------------------------------------------------
        # PHRASE BOOST
        # -------------------------------------------------

        phrase_boost = min(

            len(
                phrase_matches
            )

            *

            0.08,

            0.20

        )

        boost += phrase_boost

        # -------------------------------------------------
        # GENERIC KEYWORD
        # -------------------------------------------------

        generic_matches = [

            word

            for word in generic

            if word in text

        ]

        boost += min(

            len(
                generic_matches
            )

            *

            0.01,

            0.03

        )

        # -------------------------------------------------
        # MAXIMUM BOOST
        # -------------------------------------------------

        boost = min(

            boost,

            self.MAX_KEYWORD_BOOST

        )

        # =================================================
        # DEBUG
        # =================================================

        print()

        print(
            "KEYWORD ANALYSIS"
        )

        print(
            "Keywords:",
            keywords
        )

        print(
            "Important:",
            important
        )

        print(
            "Generic:",
            generic
        )

        print(
            "Document Matches:",
            document_matches
        )

        print(
            "Filename Matches:",
            filename_matches
        )

        print(
            "Text Matches:",
            text_matches
        )

        print(
            "Phrase Matches:",
            phrase_matches
        )

        print(
            "Coverage:",
            round(
                coverage,
                4
            )
        )

        print(
            "Important Coverage:",
            round(
                important_coverage,
                4
            )
        )

        print(
            "Keyword Boost:",
            round(
                boost,
                4
            )
        )

        return {

            "keywords":
                keywords,

            "important":
                important,

            "generic":
                generic,

            "document_matches":
                document_matches,

            "filename_matches":
                filename_matches,

            "text_matches":
                text_matches,

            "phrase_matches":
                phrase_matches,

            "coverage":
                coverage,

            "important_coverage":
                important_coverage,

            "boost":
                float(
                    boost
                )

        }

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

                analysis[
                    "document_matches"
                ]

                +

                analysis[
                    "filename_matches"
                ]

                +

                analysis[
                    "text_matches"
                ]

            )
        )

        return (

            analysis[
                "boost"
            ],

            matched_keywords

        )

    # =====================================================
    # CALCULATE FINAL SCORE
    # =====================================================

    def _calculate_final_score(
        self,
        raw_score,
        analysis
    ):

        # =================================================
        # SEMANTIC SCORE
        #
        # FAISS IndexFlatIP + normalized vectors =
        # cosine similarity.
        # =================================================

        semantic_score = max(

            0.0,

            min(

                float(
                    raw_score
                ),

                1.0

            )

        )

        # =================================================
        # KEYWORD SCORE
        #
        # Original boost:
        #
        # 0.00 - 0.40
        #
        # Normalize:
        #
        # 0.00 - 1.00
        # =================================================

        if self.MAX_KEYWORD_BOOST > 0:

            keyword_score = (

                analysis[
                    "boost"
                ]

                /

                self.MAX_KEYWORD_BOOST

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

        # =================================================
        # EVIDENCE SCORE
        #
        # Important keyword :
        # 60%
        #
        # General coverage :
        # 25%
        #
        # Phrase :
        # 15%
        # =================================================

        important_component = (

            analysis[
                "important_coverage"
            ]

            *

            0.60

        )

        coverage_component = (

            analysis[
                "coverage"
            ]

            *

            0.25

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

            /

            2

            *

            0.15

        )

        evidence_score = (

            important_component

            +

            coverage_component

            +

            phrase_component

        )

        evidence_score = max(

            0.0,

            min(

                evidence_score,

                1.0

            )

        )

        # =================================================
        # FINAL SCORE
        # =================================================

        final_score = (

            semantic_score

            *

            self.SEMANTIC_WEIGHT

        ) + (

            keyword_score

            *

            self.KEYWORD_WEIGHT

        ) + (

            evidence_score

            *

            self.EVIDENCE_WEIGHT

        )

        return {

            "semantic_score":
                float(
                    semantic_score
                ),

            "keyword_score":
                float(
                    keyword_score
                ),

            "evidence_score":
                float(
                    evidence_score
                ),

            "final_score":
                float(
                    final_score
                )

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

            if other_document != document_key:

                continue

            other_chunk_id = (
                self._get_chunk_id(
                    item
                )
            )

            chunk_distance = abs(

                other_chunk_id
                -
                chunk_id

            )

            if chunk_distance <= distance:

                neighbors.append({

                    "metadata":
                        item,

                    "index":
                        index,

                    "distance":
                        chunk_distance

                })

        return neighbors

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

        print(
            "=" * 80
        )

        print(
            "VECTOR STORE SEARCH"
        )

        print(
            "=" * 80
        )

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

            print(
                "=" * 80
            )

            return []

        # =================================================
        # METADATA CHECK
        # =================================================

        if (

            len(
                self.metadata
            )

            !=

            self.index.ntotal

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

            top_k = int(
                top_k
            )

        except Exception:

            top_k = 3

        if top_k <= 0:

            top_k = 3

        # =================================================
        # RETRIEVE MORE CANDIDATES
        # =================================================

        candidate_k = max(

            top_k
            *
            self.CANDIDATE_MULTIPLIER,

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

                "Dimensi query vector tidak sesuai. "
                f"Expected={self.dimension}, "
                f"Actual={query.shape[1]}"

            )

        # =================================================
        # NORMALIZE QUERY
        # =================================================

        faiss.normalize_L2(
            query
        )

        # =================================================
        # FAISS SEARCH
        # =================================================

        scores, indexes = self.index.search(

            query,

            candidate_k

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
        # QUESTION KEYWORDS
        # =================================================

        keywords = self._tokenize(
            question
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

            idx = int(
                idx
            )

            metadata = self.metadata[
                idx
            ]

            raw_score = float(
                raw_score
            )

            # =============================================
            # KEYWORD ANALYSIS
            # =============================================

            analysis = (
                self._analyze_keywords(
                    question,
                    metadata
                )
            )

            # =============================================
            # SCORE CALCULATION
            # =============================================

            score_data = (
                self._calculate_final_score(
                    raw_score,
                    analysis
                )
            )

            primary_candidates.append({

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

                "boost":
                    analysis[
                        "boost"
                    ],

                "analysis":
                    analysis,

                "score":
                    score_data[
                        "final_score"
                    ],

                "primary":
                    True,

                "neighbor":
                    False,

                "distance":
                    0

            })

        # =================================================
        # SORT PRIMARY
        # =================================================

        primary_candidates.sort(

            key=lambda item: (

                item[
                    "score"
                ],

                item[
                    "raw_score"
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
                ]

            ),

            reverse=True

        )

        # =================================================
        # NEIGHBOR RETRIEVAL
        #
        # Ambil neighbor dari primary candidate terbaik.
        # =================================================

        seed_count = min(

            max(

                top_k
                *
                3,

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
        # ADD PRIMARY
        # =================================================

        for item in seed_candidates:

            index = item[
                "index"
            ]

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
                    primary[
                        "metadata"
                    ]
                )
            )

            for neighbor in neighbors:

                neighbor_index = (
                    neighbor[
                        "index"
                    ]
                )

                if neighbor_index in seen_indexes:

                    continue

                neighbor_metadata = (
                    neighbor[
                        "metadata"
                    ]
                )

                # =========================================
                # ANALYZE NEIGHBOR
                # =========================================

                analysis = (
                    self._analyze_keywords(
                        question,
                        neighbor_metadata
                    )
                )

                distance = neighbor[
                    "distance"
                ]

                # =========================================
                # NEIGHBOR SEMANTIC SCORE
                #
                # Neighbor yang tidak masuk FAISS
                # candidate tidak mempunyai raw score
                # langsung dari query.
                #
                # Kita gunakan score primary terdekat
                # dengan penalty konservatif.
                # =========================================

                neighbor_raw_score = (

                    primary[
                        "raw_score"
                    ]

                    *

                    max(

                        0.0,

                        1.0

                        -

                        (
                            self.NEIGHBOR_SCORE_PENALTY
                            *
                            distance
                        )

                    )

                )

                # =========================================
                # SCORE CALCULATION
                # =========================================

                score_data = (
                    self._calculate_final_score(
                        neighbor_raw_score,
                        analysis
                    )
                )

                # =========================================
                # NEIGHBOR PENALTY
                # =========================================

                neighbor_penalty = (

                    self.NEIGHBOR_SCORE_PENALTY

                    *

                    distance

                )

                final_score = (

                    score_data[
                        "final_score"
                    ]

                    -

                    neighbor_penalty

                )

                final_score = max(

                    0.0,

                    final_score

                )

                context_candidates.append({

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
                        distance

                })

                seen_indexes.add(
                    neighbor_index
                )

        # =================================================
        # ADD REMAINING PRIMARY CANDIDATES
        #
        # Kandidat FAISS lain dengan evidence cukup
        # tetap boleh masuk context.
        # =================================================

        for item in primary_candidates:

            index = item[
                "index"
            ]

            if index in seen_indexes:

                continue

            analysis = item[
                "analysis"
            ]

            if (

                analysis[
                    "important_coverage"
                ] > 0.0

                or

                analysis[
                    "coverage"
                ] >= 0.50

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

            index = item[
                "index"
            ]

            current = unique_candidates.get(
                index
            )

            if current is None:

                unique_candidates[
                    index
                ] = item

                continue

            # ---------------------------------------------
            # Primary lebih penting daripada neighbor
            # ---------------------------------------------

            if (

                item[
                    "primary"
                ]

                and

                not current[
                    "primary"
                ]

            ):

                unique_candidates[
                    index
                ] = item

                continue

            # ---------------------------------------------
            # Score lebih tinggi menang
            # ---------------------------------------------

            if (

                item[
                    "score"
                ]

                >

                current[
                    "score"
                ]

            ):

                unique_candidates[
                    index
                ] = item

        context_candidates = list(
            unique_candidates.values()
        )

        # =================================================
        # SORT CONTEXT
        #
        # FINAL SCORE menjadi ranking utama.
        # =================================================

        context_candidates.sort(

            key=lambda item: (

                item[
                    "score"
                ],

                item[
                    "raw_score"
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

                1
                if item[
                    "primary"
                ]
                else 0,

                -item[
                    "distance"
                ]

            ),

            reverse=True

        )

        # =================================================
        # DEBUG CONTEXT
        # =================================================

        print()

        print(
            "=" * 80
        )

        print(
            "CONTEXT CANDIDATES"
        )

        print(
            "=" * 80
        )

        for rank, item in enumerate(

            context_candidates,

            start=1

        ):

            metadata = item[
                "metadata"
            ]

            analysis = item[
                "analysis"
            ]

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
                "Raw / Semantic Score:",
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
                "Keyword Boost:",
                round(
                    item[
                        "boost"
                    ],
                    4
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
                list(
                    dict.fromkeys(

                        analysis[
                            "document_matches"
                        ]

                        +

                        analysis[
                            "filename_matches"
                        ]

                        +

                        analysis[
                            "text_matches"
                        ]

                    )
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
                )[:300]
            )

        # =================================================
        # NO CANDIDATE
        # =================================================

        if not context_candidates:

            print(
                "Tidak ada candidate."
            )

            print(
                "=" * 80
            )

            return []

        # =================================================
        # BEST SCORE
        # =================================================

        best_score = context_candidates[
            0
        ][
            "score"
        ]

        # =================================================
        # RELATIVE THRESHOLD
        # =================================================

        relative_threshold = (

            best_score

            -

            self.RELATIVE_SCORE_MARGIN

        )

        # =================================================
        # ABSOLUTE THRESHOLD
        # =================================================

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

        print(
            "=" * 80
        )

        # =================================================
        # FILTER
        # =================================================

        results = []

        for rank, item in enumerate(

            context_candidates,

            start=1

        ):

            metadata = item[
                "metadata"
            ]

            score = item[
                "score"
            ]

            raw_score = item[
                "raw_score"
            ]

            boost = item[
                "boost"
            ]

            analysis = item[
                "analysis"
            ]

            matched_keywords = list(

                dict.fromkeys(

                    analysis[
                        "document_matches"
                    ]

                    +

                    analysis[
                        "filename_matches"
                    ]

                    +

                    analysis[
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
                "Raw Score:",
                round(
                    raw_score,
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
                "Boost:",
                round(
                    boost,
                    4
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
                )[:300]
            )

            # =================================================
            # SCORE FILTER
            # =================================================

            if score < threshold:

                # ---------------------------------------------
                # Strong evidence exception
                # ---------------------------------------------

                strong_evidence = (

                    analysis[
                        "important_coverage"
                    ] >= 0.75

                    or

                    analysis[
                        "coverage"
                    ] >= 0.75

                    or

                    len(
                        analysis[
                            "phrase_matches"
                        ]
                    ) >= 2

                )

                if not strong_evidence:

                    print(
                        ">>> SKIP - score terlalu rendah"
                    )

                    continue

                print(
                    ">>> KEEP - strong evidence"
                )

            # =================================================
            # BUILD RESULT
            # =================================================

            result = metadata.copy()

            result[
                "score"
            ] = round(

                score,

                4

            )

            result[
                "raw_score"
            ] = round(

                raw_score,

                4

            )

            result[
                "semantic_score"
            ] = round(

                item[
                    "semantic_score"
                ],

                4

            )

            result[
                "keyword_score"
            ] = round(

                item[
                    "keyword_score"
                ],

                4

            )

            result[
                "evidence_score"
            ] = round(

                item[
                    "evidence_score"
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
        #
        # Final score harus menjadi faktor utama.
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
                    "important_keyword_coverage"
                ],

                result[
                    "keyword_coverage"
                ],

                len(
                    result[
                        "phrase_matches"
                    ]
                )

            ),

            reverse=True

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

        print(
            "=" * 80
        )

        print(
            "FINAL SEARCH RESULT"
        )

        print(
            "=" * 80
        )

        print(
            "Result Count:",
            len(
                results
            )
        )

        for i, result in enumerate(

            results,

            start=1

        ):

            print()

            print(

                f"{i}. "
                f"{result.get('document_name', '')} "
                f"/ "
                f"{result.get('chunk_id', 0)}"

            )

            print(

                f"   Semantic Score : "
                f"{result['semantic_score']}"

            )

            print(

                f"   Keyword Score  : "
                f"{result['keyword_score']}"

            )

            print(

                f"   Evidence Score : "
                f"{result['evidence_score']}"

            )

            print(

                f"   Final Score    : "
                f"{result['score']}"

            )

            print(

                f"   Keyword Boost  : "
                f"{result['keyword_boost']}"

            )

            print(

                f"   Coverage       : "
                f"{result['keyword_coverage']}"

            )

            print(

                f"   Important Cov. : "
                f"{result['important_keyword_coverage']}"

            )

            print(

                f"   Neighbor       : "
                f"{result['neighbor']}"

            )

        print(
            "=" * 80
        )

        return results

    # =====================================================
    # SAVE
    # =====================================================

    def save(
        self
    ):

        VECTOR_INDEX.parent.mkdir(

            parents=True,

            exist_ok=True

        )

        VECTOR_METADATA.parent.mkdir(

            parents=True,

            exist_ok=True

        )

        # =================================================
        # VALIDATE BEFORE SAVE
        # =================================================

        if (

            self.index.ntotal

            !=

            len(
                self.metadata
            )

        ):

            raise RuntimeError(

                "Tidak dapat save VectorStore. "
                "Jumlah vector dan metadata tidak sama."

            )

        # =================================================
        # SAVE FAISS
        # =================================================

        faiss.write_index(

            self.index,

            str(
                VECTOR_INDEX
            )

        )

        # =================================================
        # SAVE METADATA
        # =================================================

        joblib.dump(

            self.metadata,

            VECTOR_METADATA

        )

        print()

        print(
            "=" * 60
        )

        print(
            "VECTOR STORE SAVED"
        )

        print(
            "=" * 60
        )

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
            len(
                self.metadata
            )
        )

        print(
            "=" * 60
        )

    # =====================================================
    # LOAD
    # =====================================================

    def load(
        self
    ):

        print()

        print(
            "=" * 60
        )

        print(
            "VECTOR STORE LOAD"
        )

        print(
            "=" * 60
        )

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

        print(
            "=" * 60
        )

        # =================================================
        # FILE CHECK
        # =================================================

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

        # =================================================
        # LOAD INDEX
        # =================================================

        try:

            loaded_index = faiss.read_index(

                str(
                    VECTOR_INDEX
                )

            )

        except Exception as e:

            print(
                "Gagal membaca FAISS index:"
            )

            print(
                repr(e)
            )

            return False

        # =================================================
        # DIMENSION CHECK
        # =================================================

        if (

            loaded_index.d

            !=

            self.dimension

        ):

            raise RuntimeError(

                "Dimensi FAISS index tidak sesuai. "
                f"Expected={self.dimension}, "
                f"Actual={loaded_index.d}"

            )

        # =================================================
        # LOAD METADATA
        # =================================================

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

        # =================================================
        # VALIDATE METADATA
        # =================================================

        if not isinstance(

            metadata,

            list

        ):

            raise RuntimeError(

                "Format metadata tidak valid."

            )

        # =================================================
        # VALIDATE VECTOR / METADATA
        # =================================================

        if (

            loaded_index.ntotal

            !=

            len(
                metadata
            )

        ):

            raise RuntimeError(

                "Vector dan metadata tidak sinkron. "
                f"Vector={loaded_index.ntotal}, "
                f"Metadata={len(metadata)}"

            )

        # =================================================
        # APPLY
        # =================================================

        self.index = (
            loaded_index
        )

        self.metadata = (
            metadata
        )

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
            len(
                self.metadata
            )
        )

        print(
            "=" * 60
        )

        return True

    # =====================================================
    # EMPTY
    # =====================================================

    def is_empty(
        self
    ):

        return (

            self.index.ntotal
            ==
            0

        )