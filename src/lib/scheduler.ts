import CronJob from 'node-cron';
import { db } from './db';
import { and, eq, gt } from 'drizzle-orm';
import { appointments, attendance, users } from './schema';
import doctor from '../router/doctor';

export const initScheduledJobs = () => {
    // const scheduledJobFunction = CronJob.schedule("*/10 * * * * *", async () => {
    //   console.log("I'm executed every 10 seconds!");
    //   const appointments = await getAppointmentsDueToday()
    //   console.log(appointments)
    // });

    // scheduledJobFunction.start();
}

async function getAppointmentsDueToday() {
    const atten = await db.select().from(attendance).where(eq(attendance.date, new Date()))
    const appoi = await db.select().from(appointments).where(and(gt(appointments.datetime, new Date()), eq(appointments.status, 'scheduled')))
    for(const a of atten) {
        let count = a.count
        const [doctor] = await db
            .select({
                username: users.username
            })
            .from(users)
            .where(eq(users.id, a.doctorId));
        
        const doctorName = doctor ? doctor.username : 'Unknown';
        console.log(`Processing appointments for doctor: ${doctorName}`);
        for(const b of appoi) {
            if(count < 1){
                break;
            }
            if(a.doctorId === b.doctorId && a.date >= b.datetime) {
                doSomething(b.id, a.id)
                count--
            }
    }
    const data = await db.update(attendance).set({
        count: count
    }).returning()
}
}

async function doSomething(appointmentId: number, attendanceId: number) {
    const data = await db.update(appointments).set({
        status: "appointed"
    }).returning()

}