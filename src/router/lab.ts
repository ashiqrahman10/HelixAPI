import { Hono } from 'hono';
import { jwtMiddleware } from '../middleware/jwt';
import { db } from '../lib/db';
import { labReports, users } from '../lib/schema';
import { and, eq } from 'drizzle-orm';

const lab = new Hono();

// Apply JWT middleware to all lab routes
lab.use('*', jwtMiddleware);

// Create a new lab test
lab.post('/tests', async (c) => {
  // @ts-ignore
  const labTechnicianId = c.get('jwtPayload').id;
  const { patientId, labId, testName, testDate, result, referenceRange, interpretation, notes } = await c.req.json();

  const [newLabTest] = await db.insert(labReports)
    .values({
      patientId,
      labTechnicianId,
      labId,
      testName,
      testDate: new Date(testDate),
      result,
      referenceRange,
      interpretation,
      notes,
      createdAt: new Date(),
      updatedAt: new Date(),
    })
    .returning();

  return c.json({ labTest: newLabTest });
});

// Get all lab tests
lab.get('/tests', async (c) => {
  // @ts-ignore
  const labTechnicianId = c.get('jwtPayload').id;

  const allLabTests = await db.select()
    .from(labReports)
    .where(eq(labReports.labTechnicianId, labTechnicianId));

  return c.json({ labReports: allLabTests });
});

// Get lab test by ID
lab.get('/tests/:id', async (c) => {
  // @ts-ignore
  const labTechnicianId = c.get('jwtPayload').id;
  const testId = parseInt(c.req.param('id'));

  const [labTest] = await db.select()
    .from(labReports)
    .where(and(eq(labReports.id, testId), eq(labReports.labTechnicianId, labTechnicianId)));

  if (!labTest) {
    return c.json({ error: 'Lab test not found' }, 404);
  }

  return c.json({ labTest });
});

// Update lab test
lab.put('/tests/:id', async (c) => {
  // @ts-ignore
  const labTechnicianId = c.get('jwtPayload').id;
  const testId = parseInt(c.req.param('id'));
    const { testName, testDate, result, referenceRange, interpretation, notes } = await c.req.json();

  const [updatedLabTest] = await db.update(labReports)
    .set({
      testName,
      testDate: new Date(testDate),
      result,
      referenceRange,
      interpretation,
      notes,
      updatedAt: new Date(),
    })
    .where(and(eq(labReports.id, testId), eq(labReports.labTechnicianId, labTechnicianId)))
    .returning();

  if (!updatedLabTest) {
    return c.json({ error: 'Lab test not found or not authorized' }, 404);
  }

  return c.json({ labTest: updatedLabTest });
});

// Delete lab test
lab.delete('/tests/:id', async (c) => {
  // @ts-ignore
  const labTechnicianId = c.get('jwtPayload').id;
  const testId = parseInt(c.req.param('id'));

  const [deletedLabTest] = await db.delete(labReports)
    .where(and(eq(labReports.id, testId), eq(labReports.labTechnicianId, labTechnicianId)))
    .returning();

  if (!deletedLabTest) {
    return c.json({ error: 'Lab test not found or not authorized' }, 404);
  }

  return c.json({ message: 'Lab test deleted successfully' });
});

// Update lab technician profile
lab.put('/profile', async (c) => {
  // @ts-ignore
  const labTechnicianId = c.get('jwtPayload').id;
  const { fullName, dateOfBirth, phoneNumber, address } = await c.req.json();

  const [updatedLabTechnician] = await db.update(users)
    .set({
      fullName,
      dateOfBirth: dateOfBirth ? new Date(dateOfBirth) : undefined,
      phoneNumber,
      address,
      updatedAt: new Date(),
    })
    .where(eq(users.id, labTechnicianId))
    .returning();

  return c.json({ labTechnician: { ...updatedLabTechnician, hashedPassword: undefined } });
});

export default lab;
