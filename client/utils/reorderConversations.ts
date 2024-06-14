export function reorderArray(originalArray) {
    const newArray = [];
    const queries = [];
    const responses = [];
    if (originalArray != undefined) {
        originalArray?.forEach((item) => {
            if ("query" in item) {
                queries.push(item);
            } else if ("response" in item) {
                responses.push(item);
            }
        });
    }
    for (let i = 0; i < Math.max(queries?.length, responses?.length); i++) {
        if (queries[i]) newArray?.push(queries[i]);
        if (responses[i]) newArray?.push(responses[i]);
    }
    return newArray;
}