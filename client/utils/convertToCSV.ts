export const convertToCSV = (headers: string[], rows): string => {
    const csvRows = [];

    // Add headers
    csvRows.push(headers.join(','));

    // Add rows
    for (const row of rows) {
        csvRows.push(row.join(','));
    }

    return csvRows.join('\n');
};