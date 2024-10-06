import { Hono } from 'hono';
import { jwtMiddleware } from '../middleware/jwt';
import { db } from '../lib/db';
import { documents } from '../lib/schema';
import { and, eq } from 'drizzle-orm';
import { z } from 'zod';

const document = new Hono();

// Apply JWT middleware to all document routes
document.use('*', jwtMiddleware);

// Schema for creating and updating documents
const documentSchema = z.object({
  fileName: z.string(),
  fileType: z.string().optional(),
  fileSize: z.number().optional(),
  description: z.string().optional(),
});

// Create a new document
document.post('/', async (c) => {
  // @ts-ignore
  const userId = c.get('jwtPayload').id;
  const body = await c.req.json();

  const validationResult = documentSchema.safeParse(body);
  if (!validationResult.success) {
    return c.json({ error: validationResult.error.errors }, 400);
  }

  const { fileName, fileType, fileSize, description } = validationResult.data;

  const [newDocument] = await db.insert(documents)
    .values({
      userId,
      fileName,
      fileType,
      fileSize,
      description,
    })
    .returning();

  return c.json({ document: newDocument }, 201);
});

// Get all documents for the authenticated user
document.get('/', async (c) => {
  // @ts-ignore
  const userId = c.get('jwtPayload').id;

  const userDocuments = await db.select()
    .from(documents)
    .where(and(eq(documents.userId, userId), eq(documents.isDeleted, false)));

  return c.json({ documents: userDocuments });
});

// Get a specific document by ID
document.get('/:id', async (c) => {
  // @ts-ignore
  const userId = c.get('jwtPayload').id;
  const documentId = parseInt(c.req.param('id'));

  const [userDocument] = await db.select()
    .from(documents)
    .where(and(eq(documents.id, documentId), eq(documents.userId, userId), eq(documents.isDeleted, false)));

  if (!userDocument) {
    return c.json({ error: 'Document not found' }, 404);
  }

  return c.json({ document: userDocument });
});

// Update a document
document.put('/:id', async (c) => {
  // @ts-ignore
  const userId = c.get('jwtPayload').id;
  const documentId = parseInt(c.req.param('id'));
  const body = await c.req.json();

  const validationResult = documentSchema.safeParse(body);
  if (!validationResult.success) {
    return c.json({ error: validationResult.error.errors }, 400);
  }

  const { fileName, fileType, fileSize, description } = validationResult.data;

  const [updatedDocument] = await db.update(documents)
    .set({
      fileName,
      fileType,
      fileSize,
      description,
      updatedAt: new Date(),
    })
    .where(and(eq(documents.id, documentId), eq(documents.userId, userId), eq(documents.isDeleted, false)))
    .returning();

  if (!updatedDocument) {
    return c.json({ error: 'Document not found or not authorized' }, 404);
  }

  return c.json({ document: updatedDocument });
});

// Soft delete a document
document.delete('/:id', async (c) => {
  // @ts-ignore
  const userId = c.get('jwtPayload').id;
  const documentId = parseInt(c.req.param('id'));

  const [deletedDocument] = await db.update(documents)
    .set({
      isDeleted: true,
      updatedAt: new Date(),
    })
    .where(and(eq(documents.id, documentId), eq(documents.userId, userId), eq(documents.isDeleted, false)))
    .returning();

  if (!deletedDocument) {
    return c.json({ error: 'Document not found or not authorized' }, 404);
  }

  return c.json({ message: 'Document deleted successfully', document: deletedDocument });
});

export default document;
