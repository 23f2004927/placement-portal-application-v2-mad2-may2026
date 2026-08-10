import { ref } from 'vue'
import { startExport, exportState, downloadExport } from '@/services/exports'

/*
  The export is a Celery job, so the POST only returns a task id. We poll until
  the worker reports SUCCESS, then fetch the file. Requires a running worker —
  without one this gives up after 20 tries and says so, which is the honest
  behaviour: nothing but a worker can produce the file.

  Shared by the student and company views. The endpoint picks which export to
  run from the JWT role, so neither caller says who it is.
*/
const ATTEMPTS = 20
const INTERVAL_MS = 1000

export function useExport() {
  const exporting = ref(false)
  const message = ref('')

  async function run() {
    exporting.value = true
    message.value = 'Preparing your export…'
    try {
      const { taskId } = await startExport()

      for (let attempt = 0; attempt < ATTEMPTS; attempt++) {
        await new Promise((resolve) => setTimeout(resolve, INTERVAL_MS))
        const { state } = await exportState(taskId)

        if (state === 'SUCCESS') {
          await downloadExport(taskId)
          message.value = 'Export downloaded.'
          return
        }
        if (state === 'FAILURE') {
          message.value = 'The export failed.'
          return
        }
      }
      message.value = 'Still working — is the Celery worker running?'
    } catch (err) {
      message.value = err.response?.data?.message ?? 'Could not start the export.'
    } finally {
      exporting.value = false
    }
  }

  return { exporting, message, run }
}
