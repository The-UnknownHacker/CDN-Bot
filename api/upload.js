import { writeFileSync } from "fs";
import { join } from "path";

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    const { fileName, fileContent } = req.body;

    // Validate inputs
    if (!fileName || !fileContent) {
      return res.status(400).json({ error: "Missing fileName or fileContent" });
    }

    // Decode the base64 file and save to the deployment directory
    const fileBuffer = Buffer.from(fileContent, "base64");
    const filePath = join(process.cwd(), "public", fileName);

    writeFileSync(filePath, fileBuffer);

    // Create the deployment
    const response = await fetch(
      "https://api.vercel.com/v13/deployments",
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${process.env.VERCEL_API_TOKEN}`, // Add your Vercel API token to the environment variables
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: "file-storage-bot",
          files: [
            {
              file: fileName,
              content: fileBuffer.toString("base64"),
            },
          ],
        }),
      }
    );

    const data = await response.json();

    if (response.ok) {
      const deploymentUrl = data.url
        ? `https://${data.url}/${fileName}`
        : null;

      return res.status(200).json({ url: deploymentUrl });
    } else {
      console.error("Error creating deployment:", data);
      return res.status(500).json({ error: "Deployment failed" });
    }
  } catch (error) {
    console.error("Error:", error);
    return res.status(500).json({ error: "Internal server error" });
  }
}
