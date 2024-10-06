import { z } from 'zod';

export const userCreateSchema = z.object({
  username: z.string().min(3).max(50),
  email: z.string().email(),
  password: z.string().min(8).max(100),
  fullName: z.string().min(1).max(100).optional(),
  role: z.enum(['doctor', 'patient', 'lab_technician', 'admin']).default('patient'),
  dateOfBirth: z.string().optional().refine((date) => !date || !isNaN(Date.parse(date)), {
    message: 'Invalid date format',
  }),
  phoneNumber: z.string().min(10).max(15).optional(),
  address: z.string().max(200).optional(),
});

export type UserCreate = z.infer<typeof userCreateSchema>;

// Zod schemas for input validation
export const appointmentStatusSchema = z.object({
    status: z.enum(['scheduled', 'completed', 'cancelled']),
  });
  
export const diagnosisSchema = z.object({
    patientId: z.number().int().positive(),
    diagnosis: z.string().min(1),
    date: z.string().refine((date) => !isNaN(Date.parse(date)), {
      message: 'Invalid date format',
    }),
  });
  
export const prescriptionSchema = z.object({
    patientId: z.number().int().positive(),
    medication: z.string().min(1),
    dosage: z.string().min(1),
    frequency: z.string().min(1),
    startDate: z.string().refine((date) => !isNaN(Date.parse(date)), {
      message: 'Invalid start date format',
    }),
    endDate: z.string().refine((date) => !isNaN(Date.parse(date)), {
      message: 'Invalid end date format',
    }),
  });