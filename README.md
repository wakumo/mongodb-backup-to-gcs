# mongodb-bakcup-to-gcs

## generate service account key

To generate a Google Service Account key for use with this backup solution, follow these steps:

1. Ensure you have the `gcloud` command-line tool installed and authenticated to your Google Cloud account. If not, you can install it by following the instructions here: https://cloud.google.com/sdk/docs/install

2. Set your project ID:

   ```bash
   gcloud config set project [YOUR_PROJECT_ID]
   ```

3. Create a service account:

   ```bash
   gcloud iam service-accounts create [SERVICE_ACCOUNT_NAME] --description="[DESCRIPTION]" --display-name="[DISPLAY_NAME]"
   ```

4. Grant the necessary roles to your service account (e.g., Storage Admin for managing objects in Google Cloud Storage):

   ```bash
   gcloud projects add-iam-policy-binding [YOUR_PROJECT_ID] --member="serviceAccount:[SERVICE_ACCOUNT_NAME]@[YOUR_PROJECT_ID].iam.gserviceaccount.com" --role="roles/storage.admin"
   ```

5. Generate the service account key file:

   ```bash
   gcloud iam service-accounts keys create [KEY_FILE_NAME].json --iam-account [SERVICE_ACCOUNT_NAME]@[YOUR_PROJECT_ID].iam.gserviceaccount.com
   ```

This JSON key file contains your credentials that the backup script will use to authenticate with Google Cloud services.

**Note:** Replace `[YOUR_PROJECT_ID]`, `[SERVICE_ACCOUNT_NAME]`, `[DESCRIPTION]`, `[DISPLAY_NAME]`, and `[KEY_FILE_NAME]` with your Google Cloud project ID, desired service account name, description, display name, and the name for your key file, respectively.

## generate GCP_SERVICE_ACCOUNT_KEY_BASE6 envvar

```bash
base64 -i [KEY_FILE_NAME] | pbcopy # copy to clipboard
```

```bash:.env
GCP_SERVICE_ACCOUNT_KEY_BASE64=`paste encoded txt here`
```
