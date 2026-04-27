"""
Admin Service
=============
Business logic for admin operations: dataset management, model training,
user management, and system statistics.
Uses centralized MySQL connection pool.
"""

import json
import csv
import io
from app.config import DATASET_CSV_PATH, VALID_PEMINATAN, VALID_BRAND, VALID_POSISI, VALID_LABELS
from app.ml.train import train_model
from app.database.connection import get_pool


async def get_dashboard_stats():
    """
    Get overview statistics for the admin dashboard.

    Returns:
        dict: Stats including user count, prediction count, and latest training info
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # Total users
            await cur.execute("SELECT COUNT(*) as total FROM users")
            users_count = (await cur.fetchone())["total"]

            # Total predictions
            await cur.execute("SELECT COUNT(*) as total FROM predictions")
            predictions_count = (await cur.fetchone())["total"]

            # Total dataset records
            await cur.execute("SELECT COUNT(*) as total FROM dataset_records")
            dataset_count = (await cur.fetchone())["total"]

            # Latest training log
            await cur.execute(
                "SELECT * FROM training_logs ORDER BY trained_at DESC LIMIT 1"
            )
            latest_training = await cur.fetchone()

            training_info = None
            if latest_training:
                training_info = {
                    "accuracy": latest_training["accuracy"],
                    "precision_score": latest_training["precision_score"],
                    "recall": latest_training["recall_score"],
                    "f1_score": latest_training["f1_score"],
                    "dataset_size": latest_training["dataset_size"],
                    "cv_mean_accuracy": latest_training.get("cv_mean_accuracy"),
                    "cv_std_accuracy": latest_training.get("cv_std_accuracy"),
                    "trained_at": str(latest_training["trained_at"]) if latest_training["trained_at"] else None
                }

            return {
                "total_users": users_count,
                "total_predictions": predictions_count,
                "total_dataset_records": dataset_count,
                "latest_training": training_info
            }


async def upload_dataset_csv(file_content: str):
    """
    Process and import a CSV dataset file into the database.

    Args:
        file_content: CSV file content as string

    Returns:
        dict: Result with success status and import count
    """
    try:
        reader = csv.DictReader(io.StringIO(file_content))

        # Validate headers
        required_headers = {"peminatan", "brand", "posisi", "label_sepatu"}
        if not required_headers.issubset(set(reader.fieldnames or [])):
            return {
                "success": False,
                "message": f"CSV harus memiliki kolom: {', '.join(required_headers)}"
            }

        records = []
        errors = []

        for i, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            peminatan = row["peminatan"].strip().lower()
            brand = row["brand"].strip().lower()
            posisi = row["posisi"].strip().lower()
            label = row["label_sepatu"].strip().lower()

            # Validate values
            row_errors = []
            if peminatan not in VALID_PEMINATAN:
                row_errors.append(f"peminatan '{peminatan}' tidak valid")
            if brand not in VALID_BRAND:
                row_errors.append(f"brand '{brand}' tidak valid")
            if posisi not in VALID_POSISI:
                row_errors.append(f"posisi '{posisi}' tidak valid")
            if label not in VALID_LABELS:
                row_errors.append(f"label_sepatu '{label}' tidak valid")

            if row_errors:
                errors.append(f"Baris {i}: {'; '.join(row_errors)}")
                continue

            records.append((peminatan, brand, posisi, label, "csv_upload"))

        if not records:
            return {
                "success": False,
                "message": "Tidak ada data valid ditemukan. " + " | ".join(errors[:5])
            }

        # Insert into database
        pool = get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.executemany(
                    """INSERT INTO dataset_records (peminatan, brand, posisi, label_sepatu, source)
                       VALUES (%s, %s, %s, %s, %s)""",
                    records
                )
            await conn.commit()

        # Also sync to the CSV file for training
        await _sync_dataset_to_csv()

        result = {
            "success": True,
            "message": f"Berhasil mengimpor {len(records)} data",
            "imported": len(records),
            "errors": errors[:10] if errors else []
        }
        return result

    except Exception as e:
        return {"success": False, "message": f"Error memproses CSV: {str(e)}"}


async def _sync_dataset_to_csv():
    """
    Sync all dataset records from database to the CSV file used for training.
    This ensures the training pipeline always uses the latest data.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT peminatan, brand, posisi, label_sepatu FROM dataset_records"
            )
            rows = await cur.fetchall()

        if rows:
            import os
            os.makedirs(os.path.dirname(DATASET_CSV_PATH), exist_ok=True)

            with open(DATASET_CSV_PATH, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["peminatan", "brand", "posisi", "label_sepatu"])
                writer.writeheader()
                for row in rows:
                    writer.writerow({
                        "peminatan": row["peminatan"],
                        "brand": row["brand"],
                        "posisi": row["posisi"],
                        "label_sepatu": row["label_sepatu"]
                    })


async def trigger_training():
    """
    Trigger model training and save the results to the training_logs table.

    Returns:
        dict: Training results with metrics
    """
    try:
        # Run training (synchronous ML code)
        results = train_model(csv_path=DATASET_CSV_PATH)

        # Save training log to database
        pool = get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """INSERT INTO training_logs
                       (accuracy, precision_score, recall_score, f1_score,
                        cv_mean_accuracy, cv_std_accuracy,
                        dataset_size, n_estimators,
                        classification_report, confusion_matrix, feature_importance)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        results["accuracy"],
                        results["precision"],
                        results["recall"],
                        results["f1_score"],
                        results.get("cv_mean_accuracy"),
                        results.get("cv_std_accuracy"),
                        results["dataset_size"],
                        results["n_estimators"],
                        json.dumps(results["classification_report"]),
                        json.dumps(results["confusion_matrix"]),
                        json.dumps(results["feature_importance"])
                    )
                )
            await conn.commit()

        return {
            "success": True,
            "message": "Model berhasil dilatih!",
            "metrics": {
                "accuracy": results["accuracy"],
                "precision": results["precision"],
                "recall": results["recall"],
                "f1_score": results["f1_score"],
                "cv_mean_accuracy": results.get("cv_mean_accuracy"),
                "cv_std_accuracy": results.get("cv_std_accuracy"),
                "dataset_size": results["dataset_size"],
                "feature_importance": results["feature_importance"],
                "confusion_matrix": results["confusion_matrix"],
                "class_names": results["class_names"]
            }
        }
    except FileNotFoundError as e:
        return {"success": False, "message": f"Dataset tidak ditemukan: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"Error saat training: {str(e)}"}


async def get_training_logs():
    """
    Get all training logs, ordered by most recent first.

    Returns:
        list: List of training log dicts
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT * FROM training_logs ORDER BY trained_at DESC"
            )
            rows = await cur.fetchall()

            logs = []
            for row in rows:
                logs.append({
                    "id": row["id"],
                    "accuracy": row["accuracy"],
                    "precision_score": row["precision_score"],
                    "recall": row["recall_score"],
                    "f1_score": row["f1_score"],
                    "cv_mean_accuracy": row.get("cv_mean_accuracy"),
                    "cv_std_accuracy": row.get("cv_std_accuracy"),
                    "dataset_size": row["dataset_size"],
                    "n_estimators": row["n_estimators"],
                    "feature_importance": json.loads(row["feature_importance"]) if row["feature_importance"] else {},
                    "confusion_matrix": json.loads(row["confusion_matrix"]) if row["confusion_matrix"] else [],
                    "trained_at": str(row["trained_at"]) if row["trained_at"] else None
                })

            return logs


async def get_all_users():
    """
    Get all registered users (for admin management).

    Returns:
        list: List of user dicts
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id, username, role, created_at FROM users ORDER BY created_at DESC"
            )
            rows = await cur.fetchall()
            # Serialize datetime fields
            result = []
            for row in rows:
                result.append({
                    "id": row["id"],
                    "username": row["username"],
                    "role": row["role"],
                    "created_at": str(row["created_at"]) if row["created_at"] else None
                })
            return result


async def delete_user(user_id: int):
    """
    Delete a user and their associated predictions.

    Args:
        user_id: ID of user to delete

    Returns:
        dict: Result with success status
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            # Check if user exists and is not admin
            await cur.execute(
                "SELECT role FROM users WHERE id = %s", (user_id,)
            )
            user = await cur.fetchone()

            if not user:
                return {"success": False, "message": "User tidak ditemukan"}

            if user["role"] == "admin":
                return {"success": False, "message": "Tidak dapat menghapus akun admin"}

            # Delete user (cascade will handle predictions via FK)
            await cur.execute("DELETE FROM predictions WHERE user_id = %s", (user_id,))
            await cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        await conn.commit()

        return {"success": True, "message": "User berhasil dihapus"}


async def get_dataset_records():
    """
    Get all dataset records for admin viewing.

    Returns:
        list: List of dataset record dicts
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT * FROM dataset_records ORDER BY created_at DESC LIMIT 500"
            )
            rows = await cur.fetchall()
            result = []
            for row in rows:
                result.append({
                    "id": row["id"],
                    "peminatan": row["peminatan"],
                    "brand": row["brand"],
                    "posisi": row["posisi"],
                    "label_sepatu": row["label_sepatu"],
                    "source": row["source"],
                    "created_at": str(row["created_at"]) if row["created_at"] else None
                })
            return result


async def clear_dataset():
    """
    Clear all dataset records from the database and reset the CSV file.

    Returns:
        dict: Result with success status
    """
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                # Get count before deleting
                await cur.execute("SELECT COUNT(*) as total FROM dataset_records")
                count = (await cur.fetchone())["total"]

                # Delete all dataset records
                await cur.execute("DELETE FROM dataset_records")
            await conn.commit()

        # Clear the CSV file (write header only)
        import os
        os.makedirs(os.path.dirname(DATASET_CSV_PATH), exist_ok=True)
        with open(DATASET_CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["peminatan", "brand", "posisi", "label_sepatu"])
            writer.writeheader()

        return {
            "success": True,
            "message": f"Berhasil menghapus {count} data dari dataset"
        }
    except Exception as e:
        return {"success": False, "message": f"Error menghapus dataset: {str(e)}"}


async def delete_trained_model():
    """
    Delete the trained model files (.pkl) and clear training logs.
    After this, the admin must retrain the model before predictions will work.

    Returns:
        dict: Result with success status
    """
    import os
    from app.config import MODEL_PATH, ENCODERS_PATH

    try:
        deleted_files = []

        # Delete model file
        if os.path.exists(MODEL_PATH):
            os.remove(MODEL_PATH)
            deleted_files.append("model.pkl")

        # Delete encoders file
        if os.path.exists(ENCODERS_PATH):
            os.remove(ENCODERS_PATH)
            deleted_files.append("encoders.pkl")

        # Clear training logs from database
        pool = get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT COUNT(*) as total FROM training_logs")
                log_count = (await cur.fetchone())["total"]
                await cur.execute("DELETE FROM training_logs")
            await conn.commit()

        if not deleted_files and log_count == 0:
            return {
                "success": True,
                "message": "Tidak ada model atau log training yang ditemukan"
            }

        msg_parts = []
        if deleted_files:
            msg_parts.append(f"File dihapus: {', '.join(deleted_files)}")
        if log_count > 0:
            msg_parts.append(f"{log_count} log training dihapus")

        return {
            "success": True,
            "message": "Model berhasil direset. " + ". ".join(msg_parts)
        }
    except Exception as e:
        return {"success": False, "message": f"Error menghapus model: {str(e)}"}

