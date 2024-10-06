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
