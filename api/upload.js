import { writeFileSync, unlinkSync } from 'fs';
import { join } from 'path';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { file, fileName } = req.body;
    const filePath = join('/tmp', fileName);

    // Save file temporarily
    writeFileSync(filePath, Buffer.from(file, 'base64'));

    // Generate a Vercel-hosted URL
    const publicUrl = `https://${process.env.VERCEL_URL}/${fileName}`;

    // Move file to public directory (e.g., 'public' folder)
    const targetPath = join(process.cwd(), 'public', fileName);
    writeFileSync(targetPath, Buffer.from(file, 'base64'));

    // Clean up temporary file
    unlinkSync(filePath);

    res.status(200).json({ url: publicUrl });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'File upload failed' });
  }
}
