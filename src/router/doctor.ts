import { Hono } from 'hono';
import { jwtMiddleware } from '../middleware/jwt';
import { db } from '../lib/db';
import { appointments, diagnoses, prescriptions, users } from '../lib/schema';
import { and, eq } from 'drizzle-orm';

const doctor = new Hono();

// Apply JWT middleware to all doctor routes
doctor.use('*', jwtMiddleware);

// Get doctor's appointments
doctor.get('/appointments', async (c) => {
  // @ts-ignore
  const doctorId = c.get('jwtPayload').id;

  const doctorAppointments = await db.select()
    .from(appointments)
    .where(eq(appointments.doctorId, doctorId));

  return c.json({ appointments: doctorAppointments });
});

// Get appointment by ID
doctor.get('/appointments/:id', async (c) => {
  // @ts-ignore
  const doctorId = c.get('jwtPayload').id;
  const appointmentId = parseInt(c.req.param('id'));

  const [appointment] = await db.select()
    .from(appointments)
    .where(and(eq(appointments.id, appointmentId), eq(appointments.doctorId, doctorId)));

  if (!appointment) {
    return c.json({ error: 'Appointment not found' }, 404);
  }

  return c.json({ appointment });
});

// Update appointment status
doctor.put('/appointments/:id', async (c) => {
  // @ts-ignore
  const doctorId = c.get('jwtPayload').id;
  const appointmentId = parseInt(c.req.param('id'));
  const { status } = await c.req.json();

  const [updatedAppointment] = await db.update(appointments)
    .set({
      status,
      updatedAt: new Date(),
    })
    .where(and(eq(appointments.id, appointmentId), eq(appointments.doctorId, doctorId)))
    .returning();

  if (!updatedAppointment) {
    return c.json({ error: 'Appointment not found or not authorized' }, 404);
  }

  return c.json({ appointment: updatedAppointment });
});

// Create diagnosis
doctor.post('/diagnoses', async (c) => {
  // @ts-ignore
  const doctorId = c.get('jwtPayload').id;
  const { patientId, diagnosis, date } = await c.req.json();

  const [newDiagnosis] = await db.insert(diagnoses)
    .values({
      patientId,
      doctorId,
      diagnosis,
      date: new Date(date),
      createdAt: new Date(),
      updatedAt: new Date(),
    })
    .returning();

  return c.json({ diagnosis: newDiagnosis });
});

// Get diagnoses for a specific patient
doctor.get('/diagnoses/:patientId', async (c) => {
  // @ts-ignore
  const doctorId = c.get('jwtPayload').id;
  const patientId = parseInt(c.req.param('patientId'));

  const patientDiagnoses = await db.select()
    .from(diagnoses)
    .where(and(eq(diagnoses.patientId, patientId), eq(diagnoses.doctorId, doctorId)));

  return c.json({ diagnoses: patientDiagnoses });
});

// Create prescription
doctor.post('/prescriptions', async (c) => {
  // @ts-ignore
  const doctorId = c.get('jwtPayload').id;
  const { patientId, medication, dosage, frequency, startDate, endDate } = await c.req.json();

  const [newPrescription] = await db.insert(prescriptions)
    .values({
      patientId,
      doctorId,
      medication,
      dosage,
      frequency,
      startDate: new Date(startDate),
      endDate: new Date(endDate),
      createdAt: new Date(),
      updatedAt: new Date(),
    })
    .returning();

  return c.json({ prescription: newPrescription });
});

// Get prescriptions for a specific patient
doctor.get('/prescriptions/:patientId', async (c) => {
  // @ts-ignore
  const doctorId = c.get('jwtPayload').id;
  const patientId = parseInt(c.req.param('patientId'));

  const patientPrescriptions = await db.select()
    .from(prescriptions)
    .where(and(eq(prescriptions.patientId, patientId), eq(prescriptions.doctorId, doctorId)));

  return c.json({ prescriptions: patientPrescriptions });
});

// Update doctor profile
doctor.put('/profile', async (c) => {
  // @ts-ignore
  const doctorId = c.get('jwtPayload').id;
  const { fullName, dateOfBirth, phoneNumber, address } = await c.req.json();

  const [updatedDoctor] = await db.update(users)
    .set({
      fullName,
      dateOfBirth: dateOfBirth ? new Date(dateOfBirth) : undefined,
      phoneNumber,
      address,
      updatedAt: new Date(),
    })
    .where(eq(users.id, doctorId))
    .returning();

  return c.json({ doctor: { ...updatedDoctor, hashedPassword: undefined } });
});

export default doctor;
