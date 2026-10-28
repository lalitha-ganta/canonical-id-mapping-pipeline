
import hashlib
from datetime import datetime, timezone

from src.database import get_connection


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def generate_canonical_id(email):
    normalized_email = email.strip().lower()

    hash_value = hashlib.sha256(
        normalized_email.encode("utf-8")
    ).hexdigest()[:16]

    return "CAN_" + hash_value


def process_mappings():
    conn = get_connection()

    try:
        with conn:
            records = conn.execute("""
                SELECT record_id, run_id, source_system,
                       source_id, email
                FROM source_records
                WHERE email IS NOT NULL
                ORDER BY event_time, record_id
            """).fetchall()

            matched = 0
            conflicts = 0

            for record in records:
                record_id, run_id, system, source_id, email = record

                normalized_email = email.strip().lower()

                canonical_id = generate_canonical_id(
                    normalized_email
                )

                # Check for an existing mapping
                existing = conn.execute("""
                    SELECT canonical_id
                    FROM id_mappings
                    WHERE source_system = ?
                      AND source_id = ?
                """, (system, source_id)).fetchone()

                if existing:
                    if existing[0] == canonical_id:
                        continue

                    # Different canonical ID for same source ID
                    conflict_id = hashlib.sha256(
                        (record_id + canonical_id).encode()
                    ).hexdigest()

                    conn.execute("""
                        INSERT OR IGNORE INTO mapping_conflicts (
                            conflict_id, record_id,
                            candidate_canonical_ids,
                            conflict_reason, run_id
                        )
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        conflict_id,
                        record_id,
                        f"{existing[0]},{canonical_id}",
                        "Source ID maps to multiple canonical IDs",
                        run_id
                    ))

                    conflicts += 1
                    continue

                # Create canonical entity if needed
                conn.execute("""
                    INSERT OR IGNORE INTO canonical_entities (
                        canonical_id, normalized_email, created_at
                    )
                    VALUES (?, ?, ?)
                """, (
                    canonical_id,
                    normalized_email,
                    utc_now()
                ))

                # Create source-to-canonical mapping
                conn.execute("""
                    INSERT INTO id_mappings (
                        source_system, source_id,
                        canonical_id, match_rule, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    system,
                    source_id,
                    canonical_id,
                    "NORMALIZED_EMAIL",
                    utc_now()
                ))

                matched += 1

                # Preserve mapping creation in history
                history_id = hashlib.sha256(
                    (system + "|" + source_id + "|" +
                     canonical_id).encode()
                ).hexdigest()

                conn.execute("""
                    INSERT OR IGNORE INTO mapping_history (
                        history_id, source_system, source_id,
                        old_canonical_id, new_canonical_id,
                        change_reason, changed_at, run_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    history_id,
                    system,
                    source_id,
                    None,
                    canonical_id,
                    "INITIAL_MAPPING",
                    utc_now(),
                    run_id
                ))

        print("\nCANONICAL MATCHING COMPLETED")
        print("New mappings:", matched)
        print("Conflicts detected:", conflicts)

    finally:
        conn.close()


if __name__ == "__main__":
    process_mappings()
