import { Hono } from 'hono';
import { jwtMiddleware } from '../middleware/jwt';
import { db } from '../lib/db';
import { appointments, users, doctorProfiles } from '../lib/schema';
import { and, eq } from 'drizzle-orm';
import { z } from 'zod';

const appointment = new Hono();

// Apply JWT middleware to all appointment routes
appointment.use('*', jwtMiddleware);

// Schema for creating and updating appointments
const appointmentSchema = z.object({
  doctorId: z.number(),
  date: z.string().datetime(),
  time: z.string(),
  notes: z.string().optional(),
});

// Create a new appointment
appointment.post('/', async (c) => {
  // @ts-ignore
  const userId = c.get('jwtPayload').id;
  const body = await c.req.json();
  console.log(body)

  const validationResult = appointmentSchema.safeParse(body);
  if (!validationResult.success) {
    return c.json({ error: validationResult.error.errors }, 400);
  }

  const { doctorId, date, time, notes } = validationResult.data;

  const [newAppointment] = await db.insert(appointments)
    .values({
      userId,
      doctorId,
      date: new Date(date),
      time,
      notes,
      status: 'scheduled',
    })
    .returning();

  return c.json({ appointment: newAppointment }, 201);
});

// Get all appointments for the authenticated user
appointment.get('/', async (c) => {
  // @ts-ignore
  const userId = c.get('jwtPayload').id;

  const userAppointments = await db.select({
    appointment: appointments,
    doctor: {
      id: users.id,
      fullName: users.fullName,
      specialization: doctorProfiles.specialization,
    },
  })
    .from(appointments)
    .where(eq(appointments.userId, userId))
    .leftJoin(users, eq(appointments.doctorId, users.id))
    .leftJoin(doctorProfiles, eq(users.id, doctorProfiles.userId));

  return c.json({ appointments: userAppointments });
});

// Get a specific appointment by ID
appointment.get('/:id', async (c) => {
  // @ts-ignore
  const userId = c.get('jwtPayload').id;
  const appointmentId = parseInt(c.req.param('id'));

  const [userAppointment] = await db.select({
    appointment: appointments,
    doctor: {
      id: users.id,
      fullName: users.fullName,
      specialization: doctorProfiles.specialization,
    },
  })
    .from(appointments)
    .where(and(eq(appointments.id, appointmentId), eq(appointments.userId, userId)))
    .leftJoin(users, eq(appointments.doctorId, users.id))
    .leftJoin(doctorProfiles, eq(users.id, doctorProfiles.userId));

  if (!userAppointment) {
    return c.json({ error: 'Appointment not found' }, 404);
  }

  return c.json({ appointment: userAppointment });
});

// Update an appointment
appointment.put('/:id', async (c) => {
  // @ts-ignore
  const userId = c.get('jwtPayload').id;
  const appointmentId = parseInt(c.req.param('id'));
  const body = await c.req.json();

  const validationResult = appointmentSchema.safeParse(body);
  if (!validationResult.success) {
    return c.json({ error: validationResult.error.errors }, 400);
  }

  const { doctorId, date, time, notes } = validationResult.data;

  const [updatedAppointment] = await db.update(appointments)
    .set({
      doctorId,
      date: new Date(date),
      time,
      notes,
      updatedAt: new Date(),
    })
    .where(and(eq(appointments.id, appointmentId), eq(appointments.userId, userId)))
    .returning();

  if (!updatedAppointment) {
    return c.json({ error: 'Appointment not found or not authorized' }, 404);
  }

  return c.json({ appointment: updatedAppointment });
});

// Cancel an appointment
appointment.delete('/:id', async (c) => {
  // @ts-ignore
  const userId = c.get('jwtPayload').id;
  const appointmentId = parseInt(c.req.param('id'));

  const [cancelledAppointment] = await db.update(appointments)
    .set({
      status: 'cancelled',
      updatedAt: new Date(),
    })
    .where(and(eq(appointments.id, appointmentId), eq(appointments.userId, userId)))
    .returning();

  if (!cancelledAppointment) {
    return c.json({ error: 'Appointment not found or not authorized' }, 404);
  }

  return c.json({ message: 'Appointment cancelled successfully', appointment: cancelledAppointment });
});

export default appointment;
