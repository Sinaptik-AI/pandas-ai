'use server'
import { revalidateTag } from 'next/cache'

export async function revalidateDatasets() {
    revalidateTag('GetDatasetDetails')
    revalidateTag('GetAllDataSets')
}

export async function revalidateLogs() {
    revalidateTag('GetLogs')
    revalidateTag('GetLogDetails')
}