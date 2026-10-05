import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to sys.path
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
sys.path.insert(0, project_root)

try:
    from ai.utils.sf_auth import get_snowflake_conn
except ImportError:
    logger.error("Could not import ai.utils.sf_auth. Ensure you are running this script from the correct directory.")
    sys.exit(1)

def upload_images(stage_name="PROFILE_IMAGES_STAGE"):
    """
    Uploads all images from the local user_images directory to the specified Snowflake stage.
    """
    upload_dir = os.path.join(project_root, "ai", "data_generation", "user_images")
    if not os.path.exists(upload_dir):
        logger.error(f"Upload directory not found: {upload_dir}")
        return

    logger.info("Connecting to Snowflake...")
    try:
        sf_conn = get_snowflake_conn()
    except Exception as e:
        logger.error(f"Could not connect to Snowflake: {e}")
        return

    cursor = sf_conn.cursor()

    try:
        # Ensure the stage exists
        cursor.execute(f"CREATE STAGE IF NOT EXISTS {stage_name}")
        logger.info(f"Stage '{stage_name}' is ready.")

        logger.info(f"Uploading files from {upload_dir} to stage @{stage_name}...")
        
        # Get all files in the directory
        files_to_upload = [f for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]
        
        if not files_to_upload:
            logger.warning("No files found to upload in the directory.")
            return

        for filename in files_to_upload:
            file_path = os.path.join(upload_dir, filename).replace("\\", "/")
            
            # PUT command
            query = f"PUT 'file://{file_path}' @{stage_name} AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
            logger.info(f"Uploading {filename}...")
            cursor.execute(query)
            
        logger.info(f"Upload complete. {len(files_to_upload)} files uploaded to @{stage_name}.")

    except Exception as e:
        logger.error(f"Error during upload to stage @{stage_name}: {e}")
    finally:
        cursor.close()
        sf_conn.close()
        logger.info("Snowflake connection closed.")

if __name__ == "__main__":
    upload_images()
