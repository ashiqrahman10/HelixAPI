import { Hono } from 'hono';
import { jwtMiddleware } from '../middleware/jwt';
import { initializeApp } from 'firebase/app';
import { getStorage, ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { firebaseConfig } from '../lib/firebase-config';

// Initialize Firebase
const firebaseApp = initializeApp(firebaseConfig);
const storage = getStorage(firebaseApp);

const file = new Hono();

// Apply JWT middleware to all file routes
file.use('*', jwtMiddleware);

// Upload file endpoint

file.post('/upload', async (c) => {
    try {
      // @ts-ignore
      const userId = c.get('jwtPayload').id;
      
      // Get the raw body as an ArrayBuffer
      const form = await c.req.formData();
      const file = form.get('file') as File;

      if (!file) {
        return c.json({ error: 'No file provided' }, 400);
      }
  
      // Get the filename from the Content-Disposition header, if available
      const fileName = file.name;
  
      // Generate a unique file name
      const uniqueFileName = `${Date.now()}_${fileName}`;
      const filePath = `uploads/${userId}/${uniqueFileName}`;
  
      // Create a reference to the file location in Firebase Storage
      const storageRef = ref(storage, filePath);
  
      // Upload the file
      await uploadBytes(storageRef, file);
  
      // Get the download URL
      const downloadURL = await getDownloadURL(storageRef);
  
      return c.json({ 
        message: 'File uploaded successfully',
        fileName: uniqueFileName,
        downloadURL: downloadURL
      });
    } catch (error) {
      console.error('Error uploading file:', error);
      return c.json({ 
        error: 'Failed to upload file', 
        details: error instanceof Error ? error.message : String(error)
      }, 500);
    }
  });



export default file;
