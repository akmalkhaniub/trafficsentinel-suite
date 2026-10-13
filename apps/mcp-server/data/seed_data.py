"""
AdStream MCP — Synthetic Telemetry & Parquet Data Generator
Creates realistic Parquet datasets for ad-tech IVT investigations and benchmarks.
"""

import os
import duckdb
import datetime

def generate_telemetry_parquet(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    conn = duckdb.connect()

    print("[*] Generating synthetic publisher_ivt_daily dataset...")
    conn.execute(f"""
        CREATE TABLE publisher_ivt AS
        SELECT 
            ('2026-09-01'::DATE + INTERVAL (i % 30) DAY)::DATE AS date,
            'pub_' || lpad((i % 100)::VARCHAR, 4, '0') AS publisher_id,
            CASE 
                WHEN (i % 100) = 42 THEN 'stream-bad-actor.net'
                WHEN (i % 100) = 88 THEN 'ad-laundering-media.com'
                ELSE 'premium-publisher-' || (i % 100)::VARCHAR || '.com'
            END AS domain,
            (100000 + (i * 231) % 400000)::BIGINT AS total_impressions,
            CASE 
                WHEN (i % 100) IN (42, 88) THEN (30000 + (i * 50) % 20000)::BIGINT
                ELSE (95000 + (i * 220) % 380000)::BIGINT
            END AS valid_impressions,
            (2000 + (i * 13) % 8000)::BIGINT AS givt_impressions,
            CASE 
                WHEN (i % 100) = 42 THEN 45000::BIGINT
                WHEN (i % 100) = 88 THEN 62000::BIGINT
                ELSE (1000 + (i * 7) % 3000)::BIGINT
            END AS sivt_impressions,
            CASE 
                WHEN (i % 100) = 42 THEN 'hidden_ad_webview'
                WHEN (i % 100) = 88 THEN 'session_hijacking'
                ELSE 'benign'
            END AS top_sivt_category
        FROM range(3000) t(i);
        
        COPY (
            SELECT 
                *,
                round(givt_impressions::DOUBLE / total_impressions, 4) AS givt_rate,
                round(sivt_impressions::DOUBLE / total_impressions, 4) AS sivt_rate
            FROM publisher_ivt
        ) TO '{os.path.join(output_dir, "publisher_ivt_daily.parquet").replace('\\', '/')}' (FORMAT PARQUET);
    """)

    print("[*] Generating synthetic ctv_app_telemetry dataset...")
    conn.execute(f"""
        CREATE TABLE ctv_telemetry AS
        SELECT 
            CASE (i % 4)
                WHEN 0 THEN 'com.streammaster.roku'
                WHEN 1 THEN 'com.firetv.cinemahub'
                WHEN 2 THEN 'tv.appletv.kidsplay'
                ELSE 'com.androidtv.streamio.' || (i % 20)::VARCHAR
            END AS bundle_id,
            CASE (i % 4)
                WHEN 0 THEN 'roku'
                WHEN 1 THEN 'firetv'
                WHEN 2 THEN 'appletv'
                ELSE 'androidtv'
            END AS platform,
            CASE (i % 4)
                WHEN 0 THEN 'StreamMaster Free Movies'
                WHEN 1 THEN 'CinemaHub 4K'
                WHEN 2 THEN 'KidsPlay Learning ABC'
                ELSE 'StreamIO Player ' || (i % 20)::VARCHAR
            END AS app_name,
            (50000 + (i * 123) % 250000)::INT AS daily_active_devices,
            CASE 
                WHEN (i % 4) = 0 THEN 0.68  -- 68% background screensaver playback (Heavy SIVT Fraud!)
                WHEN (i % 4) = 1 THEN 0.12  -- Normal CTV playback
                ELSE 0.02
            END AS screensaver_playback_ratio,
            CASE 
                WHEN (i % 4) = 0 THEN 0.94  -- High UA entropy (spoofed device headers)
                ELSE 0.15
            END AS user_agent_entropy_score,
            CASE 
                WHEN (i % 4) = 0 THEN 4     -- Only 4 proxy IPs for all 50k devices (SSAI proxy fraud)
                ELSE 380
            END AS ssai_server_ip_diversity,
            CASE (i % 4)
                WHEN 2 THEN TRUE            -- Child-directed
                ELSE FALSE
            END AS is_kid_directed,
            CASE (i % 4)
                WHEN 2 THEN FALSE           -- Non-compliant with COPPA! (Transmits IDFA)
                ELSE TRUE
            END AS coppa_compliant,
            CURRENT_TIMESTAMP AS last_audited_timestamp
        FROM range(25) t(i);

        COPY ctv_telemetry TO '{os.path.join(output_dir, "ctv_app_telemetry.parquet").replace('\\', '/')}' (FORMAT PARQUET);
    """)

    print("[*] Generating synthetic bidstream_auction_anomalies dataset...")
    conn.execute(f"""
        CREATE TABLE bidstream_anomalies AS
        SELECT 
            'anom_' || lpad(i::VARCHAR, 5, '0') AS id,
            CURRENT_TIMESTAMP - INTERVAL (i * 10) MINUTE AS timestamp,
            'seller_' || lpad((i % 15)::VARCHAR, 3, '0') AS seller_id,
            'openx_exchange_' || (i % 3)::VARCHAR AS exchange_id,
            CASE (i % 3)
                WHEN 0 THEN 'bid_duplication'
                WHEN 1 THEN 'ip_cluster'
                ELSE 'geo_mismatch'
            END AS anomaly_type,
            CASE (i % 3)
                WHEN 0 THEN 0.35 + (i % 20)::DOUBLE / 100.0
                ELSE 0.05
            END AS duplicated_bid_ratio,
            '194.26.29.0/24' AS suspicious_cidr_prefix,
            0.85 + ((i % 15)::DOUBLE / 100.0) AS anomaly_confidence
        FROM range(500) t(i);

        COPY bidstream_anomalies TO '{os.path.join(output_dir, "bidstream_anomalies.parquet").replace('\\', '/')}' (FORMAT PARQUET);
    """)

    conn.close()
    print(f"[OK] All Parquet datasets successfully generated in: {output_dir}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    generate_telemetry_parquet(current_dir)
