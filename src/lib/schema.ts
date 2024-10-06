import { sqliteTable, text, integer, real } from 'drizzle-orm/sqlite-core';

export const users = sqliteTable('users', {
  id: integer('id').primaryKey(),
  username: text('username').notNull().unique(),
  email: text('email').notNull().unique(),
  hashedPassword: text('hashed_password').notNull(),
  fullName: text('full_name'),
  role: text('role', { enum: ['doctor', 'patient', 'lab_technician', 'admin'] }).default('patient'),
  dateOfBirth: integer('date_of_birth', { mode: 'timestamp' }),
  phoneNumber: text('phone_number'),
  address: text('address'),
  createdAt: integer('created_at', { mode: 'timestamp' }).defaultNow(),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).defaultNow(),
});

export const doctorProfiles = sqliteTable('doctors', {
  id: integer('id').primaryKey(),
  userId: integer('user_id').notNull().references(() => users.id),
  specialization: text('specialization'),
  licenseNumber: text('license_number').unique(),
  yearsOfExperience: integer('years_of_experience'),
});

export const labTechnicianProfiles = sqliteTable('lab_technicians', {
  id: integer('id').primaryKey(),
  userId: integer('user_id').notNull().references(() => users.id),
  yearsOfExperience: integer('years_of_experience'),
});

export const appointments = sqliteTable('appointments', {
  id: integer('id').primaryKey(),
  userId: integer('user_id').notNull().references(() => users.id),
  doctorId: integer('doctor_id').notNull().references(() => doctorProfiles.id),
  datetime: integer('date', { mode: 'timestamp' }).notNull(),
  status: text('status', { enum: ['scheduled', 'completed', 'cancelled', "appointed"] }).default('scheduled'),
  notes: text('notes'),
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull().defaultNow(),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).notNull().defaultNow(),
});

export const diagnoses = sqliteTable('diagnoses', {
  id: integer('id').primaryKey(),
  patientId: integer('patient_id').notNull().references(() => users.id),
  doctorId: integer('doctor_id').notNull().references(() => doctorProfiles.id),
  diagnosis: text('diagnosis').notNull(),
  date: integer('date', { mode: 'timestamp' }).notNull(),
  notes: text('notes'),
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull().defaultNow(),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).notNull().defaultNow(),
});

export const prescriptions = sqliteTable('prescriptions', {
  id: integer('id').primaryKey(),
  patientId: integer('patient_id').notNull().references(() => users.id),
  doctorId: integer('doctor_id').notNull().references(() => doctorProfiles.id),
  medication: text('medication').notNull(),
  dosage: text('dosage').notNull(),
  frequency: text('frequency').notNull(),
  startDate: integer('start_date', { mode: 'timestamp' }).notNull(),
  endDate: integer('end_date', { mode: 'timestamp' }).notNull(),
  notes: text('notes'),
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull().defaultNow(),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).notNull().defaultNow(),
});

export const labs = sqliteTable('labs', {
  id: integer('id').primaryKey(),
  labTechnicianId: integer('lab_technician_id').notNull().references(() => labTechnicianProfiles.id),
  name: text('name').notNull(),
  address: text('address'),
  phoneNumber: text('phone_number'),
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull().defaultNow(),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).notNull().defaultNow(),
});

export const labEquipment = sqliteTable('lab_equipment', {
  id: integer('id').primaryKey(),
  labId: integer('lab_id').notNull().references(() => labs.id),
  name: text('name').notNull(),
  model: text('model'),
  serialNumber: text('serial_number').unique(),
  purchaseDate: integer('purchase_date', { mode: 'timestamp' }),
  lastMaintenanceDate: integer('last_maintenance_date', { mode: 'timestamp' }),
  status: text('status', { enum: ['operational', 'under_maintenance', 'out_of_order'] }).default('operational'),
  notes: text('notes'),
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull().defaultNow(),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).notNull().defaultNow(),
});

export const labReports = sqliteTable('lab_reports', {
  id: integer('id').primaryKey(),
  labId: integer('lab_id').notNull().references(() => labs.id),
  patientId: integer('patient_id').notNull().references(() => users.id),
  labTechnicianId: integer('lab_technician_id').notNull().references(() => labTechnicianProfiles.id),
  testName: text('test_name').notNull(),
  testDate: integer('test_date', { mode: 'timestamp' }).notNull(),
  result: text('result').notNull(),
  referenceRange: text('reference_range'),
  interpretation: text('interpretation'),
  notes: text('notes'),
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull().defaultNow(),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).notNull().defaultNow(),
});

export const attendance = sqliteTable('attendance', {
  id: integer('id').primaryKey(),
  doctorId: integer('doctor_id').notNull().references(() => users.id),
  date: integer('date', { mode: 'timestamp' }).notNull(),
  count: integer('count').notNull().default(6),
  notes: text('notes'),
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull().defaultNow(),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).notNull().defaultNow(),
});

export const nutritionalPlans = sqliteTable('nutritional_plans', {
  id: integer('id').primaryKey(),
  patientId: integer('patient_id').notNull().references(() => users.id),
  doctorId: integer('doctor_id').notNull().references(() => users.id),
  planDetails: text('plan_details').notNull(),
  startDate: integer('start_date', { mode: 'timestamp' }).notNull(),
  endDate: integer('end_date', { mode: 'timestamp' }),
  goals: text('goals'),
  notes: text('notes'),
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull().defaultNow(),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).notNull().defaultNow(),
});

export const documents = sqliteTable('documents', {
  id: integer('id').primaryKey(),
  userId: integer('user_id').notNull().references(() => users.id),
  fileName: text('file_name').notNull(),
  fileType: text('file_type'),
  fileSize: integer('file_size'),
  uploadDate: integer('upload_date', { mode: 'timestamp' }).notNull().defaultNow(),
  description: text('description'),
  isDeleted: integer('is_deleted', { mode: 'boolean' }).default(false),
  createdAt: integer('created_at', { mode: 'timestamp' }).notNull().defaultNow(),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).notNull().defaultNow(),
});
