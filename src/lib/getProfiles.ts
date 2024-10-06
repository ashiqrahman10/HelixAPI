import { db } from './db';
import { users, doctorProfiles } from './schema';
import { eq } from 'drizzle-orm';

export async function getUserAndDoctorProfile(userId: number) {
  const [user] = await db
    .select()
    .from(users)
    .where(eq(users.id, userId));

  if (!user) {
    return null;
  }

  if (user.role !== 'doctor') {
    return null
  }

  const [doctorProfile] = await db
    .select()
    .from(doctorProfiles)
    .where(eq(doctorProfiles.userId, userId));

  return {
    ...user,
    hashedPassword: undefined,
    doctorProfile: doctorProfile || null,
  };
}
