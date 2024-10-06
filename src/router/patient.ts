import { Hono } from 'hono';
import { jwtMiddleware } from '../middleware/jwt';
import { db } from '../lib/db';
import { users, medications } from '../lib/schema';
import { eq } from 'drizzle-orm';

const patient = new Hono();

// Apply JWT middleware to all patient routes
patient.use('*', jwtMiddleware);

// Get patient's appointments
patient.get('/appointments', async (c) => {
  // @ts-ignore
  const userId = c.get('jwtPayload').id;

  const patientAppointments = await db.select()
    .from(appointments)
    .where(eq(appointments.userId, userId));

  return c.json({ appointments: patientAppointments });
});

// Get patient's diagnoses
patient.get('/diagnoses', async (c) => {
  // @ts-ignore
  const userId = c.get('jwtPayload').id;

  const patientDiagnoses = await db.select()
    .from(diagnoses)
    .where(eq(diagnoses.patientId, userId));

  return c.json({ diagnoses: patientDiagnoses });
});

// Get patient's prescriptions
patient.get('/prescriptions', async (c) => {
  // @ts-ignore
  const userId = c.get('jwtPayload').id;

  const patientPrescriptions = await db.select()
    .from(prescriptions)
    .where(eq(prescriptions.patientId, userId));

  return c.json({ prescriptions: patientPrescriptions });
});

// Update patient profile
patient.put('/profile', async (c) => {
  // @ts-ignore
  const userId = c.get('jwtPayload').id;
  const { fullName, dateOfBirth, phoneNumber, address } = await c.req.json();

  const [updatedUser] = await db.update(users)
    .set({
      fullName,
      dateOfBirth: dateOfBirth ? new Date(dateOfBirth) : undefined,
      phoneNumber,
      address,
      updatedAt: new Date(),
    })
    .where(eq(users.id, userId))
    .returning();

  return c.json({ user: { ...updatedUser, hashedPassword: undefined } });
});

export default patient;
