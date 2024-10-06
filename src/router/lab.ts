import { Hono } from 'hono';
import { jwtMiddleware } from '../middleware/jwt';
import { db } from '../lib/db';
import { labReports, users } from '../lib/schema';
import { and, eq } from 'drizzle-orm';
import { getUserAndLabTechnicianProfile } from '../lib/getProfiles';

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


// Get lab technician profile
lab.get('/profile', async (c) => {
  // @ts-ignore
  const labTechnicianId = c.get('jwtPayload').id;

  const labTechnician = await getUserAndLabTechnicianProfile(labTechnicianId);

  if (!labTechnician) {
    return c.json({ error: 'Lab technician profile not found' }, 404);
  }

  return c.json({ labTechnician });
});


export default lab;
