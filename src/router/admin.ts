import { Hono } from 'hono';
import { jwtMiddleware } from '../middleware/jwt';
import { db } from '../lib/db';
import { users, appointments, diagnoses, prescriptions, doctorProfiles } from '../lib/schema';
import { eq } from 'drizzle-orm';

const admin = new Hono();

// Apply JWT middleware to all admin routes
admin.use('*', jwtMiddleware);

// Middleware to check if the user is an admin
const adminMiddleware = async (c: any, next: any) => {
  const userId = c.get('jwtPayload').id;
  const [user] = await db.select().from(users).where(eq(users.id, userId));
  
  if (!user || user.role !== 'admin') {
    return c.json({ error: 'Unauthorized' }, 403);
  }
  
  await next();
};

admin.use('*', adminMiddleware);

// Get all users
admin.get('/users', async (c) => {
  const allUsers = await db.select().from(users);
  return c.json({ users: allUsers.map(user => ({ ...user, hashedPassword: undefined })) });
});

// Get user by ID
admin.get('/users/:id', async (c) => {
  const userId = parseInt(c.req.param('id'));
  const [user] = await db.select().from(users).where(eq(users.id, userId));
  
  if (!user) {
    return c.json({ error: 'User not found' }, 404);
  }
  
  return c.json({ user: { ...user, hashedPassword: undefined } });
});

// Update user
admin.put('/users/:id', async (c) => {
  const userId = parseInt(c.req.param('id'));
  const { fullName, email, role, dateOfBirth, phoneNumber, address } = await c.req.json();
  
  const [updatedUser] = await db.update(users)
    .set({
      fullName,
      email,
      role,
      dateOfBirth: dateOfBirth ? new Date(dateOfBirth) : undefined,
      phoneNumber,
      address,
      updatedAt: new Date(),
    })
    .where(eq(users.id, userId))
    .returning();
  
  return c.json({ user: { ...updatedUser, hashedPassword: undefined } });
});

// Delete user
admin.delete('/users/:id', async (c) => {
  const userId = parseInt(c.req.param('id'));
  await db.delete(users).where(eq(users.id, userId));
  return c.json({ message: 'User deleted successfully' });
});

// Get all appointments
admin.get('/appointments', async (c) => {
  const allAppointments = await db.select().from(appointments);
  return c.json({ appointments: allAppointments });
});

// Get appointment by ID
admin.get('/appointments/:id', async (c) => {
  const appointmentId = parseInt(c.req.param('id'));
  const [appointment] = await db.select().from(appointments).where(eq(appointments.id, appointmentId));
  
  if (!appointment) {
    return c.json({ error: 'Appointment not found' }, 404);
  }
  
  return c.json({ appointment });
});

// Update appointment
admin.put('/appointments/:id', async (c) => {
  const appointmentId = parseInt(c.req.param('id'));
  const { userId, doctorId, dateTime, status } = await c.req.json();
  
  const [updatedAppointment] = await db.update(appointments)
    .set({
      userId,
      doctorId,
      date: new Date(dateTime),
      status,
      updatedAt: new Date(),
    })
    .where(eq(appointments.id, appointmentId))
    .returning();
  
  return c.json({ appointment: updatedAppointment });
});

// Delete appointment
admin.delete('/appointments/:id', async (c) => {
  const appointmentId = parseInt(c.req.param('id'));
  await db.delete(appointments).where(eq(appointments.id, appointmentId));
  return c.json({ message: 'Appointment deleted successfully' });
});

// Get all diagnoses
admin.get('/diagnoses', async (c) => {
  const allDiagnoses = await db.select().from(diagnoses);
  return c.json({ diagnoses: allDiagnoses });
});

// Get diagnosis by ID
admin.get('/diagnoses/:id', async (c) => {
  const diagnosisId = parseInt(c.req.param('id'));
  const [diagnosis] = await db.select().from(diagnoses).where(eq(diagnoses.id, diagnosisId));
  
  if (!diagnosis) {
    return c.json({ error: 'Diagnosis not found' }, 404);
  }
  
  return c.json({ diagnosis });
});

// Update diagnosis
admin.put('/diagnoses/:id', async (c) => {
  const diagnosisId = parseInt(c.req.param('id'));
  const { patientId, doctorId, diagnosis, date } = await c.req.json();
  
  const [updatedDiagnosis] = await db.update(diagnoses)
    .set({
      patientId,
      doctorId,
      diagnosis,
      date: new Date(date),
      updatedAt: new Date(),
    })
    .where(eq(diagnoses.id, diagnosisId))
    .returning();
  
  return c.json({ diagnosis: updatedDiagnosis });
});

// Delete diagnosis
admin.delete('/diagnoses/:id', async (c) => {
  const diagnosisId = parseInt(c.req.param('id'));
  await db.delete(diagnoses).where(eq(diagnoses.id, diagnosisId));
  return c.json({ message: 'Diagnosis deleted successfully' });
});

// Get all prescriptions
admin.get('/prescriptions', async (c) => {
  const allPrescriptions = await db.select().from(prescriptions);
  return c.json({ prescriptions: allPrescriptions });
});

// Get prescription by ID
admin.get('/prescriptions/:id', async (c) => {
  const prescriptionId = parseInt(c.req.param('id'));
  const [prescription] = await db.select().from(prescriptions).where(eq(prescriptions.id, prescriptionId));
  
  if (!prescription) {
    return c.json({ error: 'Prescription not found' }, 404);
  }
  
  return c.json({ prescription });
});

// Update prescription
admin.put('/prescriptions/:id', async (c) => {
  const prescriptionId = parseInt(c.req.param('id'));
  const { patientId, doctorId, medication, dosage, frequency, startDate, endDate } = await c.req.json();
  
  const [updatedPrescription] = await db.update(prescriptions)
    .set({
      patientId,
      doctorId,
      medication,
      dosage,
      frequency,
      startDate: new Date(startDate),
      endDate: endDate ? new Date(endDate) : undefined,
      updatedAt: new Date(),
    })
    .where(eq(prescriptions.id, prescriptionId))
    .returning();
  
  return c.json({ prescription: updatedPrescription });
});

// Delete prescription
admin.delete('/prescriptions/:id', async (c) => {
  const prescriptionId = parseInt(c.req.param('id'));
  await db.delete(prescriptions).where(eq(prescriptions.id, prescriptionId));
  return c.json({ message: 'Prescription deleted successfully' });
});

// Change user role from patient to doctor and create doctor profile
admin.post('/change-to-doctor/:id', async (c) => {
  const userId = parseInt(c.req.param('id'));
  const { specialization, licenseNumber } = await c.req.json();

  // Validate input
  if (!specialization || !licenseNumber) {
    return c.json({ error: 'Specialization and license number are required' }, 400);
  }

  // Start a transaction
  const result = await db.transaction(async (tx) => {
    // Update user role
    const [updatedUser] = await tx.update(users)
      .set({ role: 'doctor', updatedAt: new Date() })
      .where(eq(users.id, userId))
      .returning();

    if (!updatedUser) {
      throw new Error('User not found');
    }

    // Create doctor profile
    const [newDoctorProfile] = await tx.insert(doctorProfiles)
      .values({
        userId,
        specialization,
        licenseNumber,
      })
      .returning();

    return { user: updatedUser, doctorProfile: newDoctorProfile };
  });

  return c.json({ message: 'User role changed to doctor and profile created', data: result });
});


export default admin;
