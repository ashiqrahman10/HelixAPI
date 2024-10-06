
import { serve } from '@hono/node-server'
import { Hono } from 'hono'
import authRouter from './router/auth'
import patientRouter from './router/patient'
import adminRouter from './router/admin'
import appointmentRouter from './router/appointment'
import doctorRouter from './router/doctor'
import documentRouter from './router/documents'
// Load environment variables from .env file

type Variables = {
  "jwtPayload": {
    id: number
  } | null
}

const app = new Hono<{ Variables: Variables }>()

app.get('/', (c) => {
  return c.text('Hello Hono!')
})

app.route('/auth', authRouter)
app.route('/patient', patientRouter)
app.route('/admin', adminRouter)
app.route('/appointment', appointmentRouter)
app.route('/doctor', doctorRouter)
app.route('/document', documentRouter)


const port = process.env.PORT ? parseInt(process.env.PORT) : 3000
console.log(`Server is running on port ${port}`)

serve({
  fetch: app.fetch,
  port
})
