import fs from 'fs';
import https from 'https';
import dotenv from 'dotenv';

// Fetches configuration from S3 and writes private.key and .env files
export async function fetchAndWriteEnvAndKey() {
  const url = 'https://dropi-front-end-bucket.s3.us-east-1.amazonaws.com/keys.json';

  return new Promise((resolve, reject) => {
    https.get(url, (resp) => {
      let data = '';

      resp.on('data', (chunk) => { data += chunk; });

      resp.on('end', () => {
        try {
          const json = JSON.parse(data);
          let envContent = '';

          // Write private.key
          if ('private_key' in json) {
            const privateKey = json['private_key'];
            const privateKeyPath = process.env.PRIVATE_KEY_PATH || 'private.key';

            try {
              fs.writeFileSync(privateKeyPath, privateKey, { mode: 0o600 });
              console.log(`private.key written successfully at ${privateKeyPath}`);
            } catch (writeError) {
              if (writeError.code === 'EROFS' || writeError.code === 'EACCES') {
                console.warn(`Cannot write ${privateKeyPath}: filesystem is read-only. Make sure private.key is mounted as volume.`);
                // Store in environment variable as fallback
                process.env.PRIVATE_KEY_CONTENT = privateKey;
              } else {
                throw writeError;
              }
            }
            delete json['private_key'];
          }

          // Write .env file with all other variables
          Object.keys(json).forEach(key => {
            const value = json[key];
            // Convert value to string and escape if necessary
            let envValue = String(value);
            // If value contains spaces, quotes, or special characters, wrap in quotes
            if (envValue.includes(' ') || envValue.includes('"') || envValue.includes("'") || envValue.includes('\n')) {
              // Escape quotes and wrap in double quotes
              envValue = `"${envValue.replace(/"/g, '\\"')}"`;
            }
            envContent += `${key}=${envValue}\n`;
          });

          try {
            if (envContent.trim()) {
              // Write .env file with proper encoding
              fs.writeFileSync('.env', envContent, { mode: 0o644, encoding: 'utf8' });
              console.log('.env written successfully');
              console.log(`Variables written: ${Object.keys(json).join(', ')}`);
            }
            
            // Set environment variables directly in process.env (important for Docker)
            Object.keys(json).forEach(key => {
              process.env[key] = String(json[key]);
            });
            
            // Reload dotenv to ensure all variables are available
            dotenv.config({ override: true });
            
            resolve();
          } catch (writeError) {
            if (writeError.code === 'EROFS' || writeError.code === 'EACCES') {
              console.warn('Cannot write .env: filesystem is read-only. Using environment variables directly.');
              // Set environment variables directly
              Object.keys(json).forEach(key => {
                process.env[key] = String(json[key]);
              });
              resolve();
            } else {
              throw writeError;
            }
          }
        } catch (err) {
          console.error('Error processing JSON:', err);
          reject(err);
        }
      });

    }).on("error", (err) => {
      console.log("Error: " + err.message);
      reject(err);
    });
  });
}
