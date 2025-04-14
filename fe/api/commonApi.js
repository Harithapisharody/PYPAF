// commonApi.js
async function postData(endpoint, body) {
    try {
        const response = await fetch(`${baseURL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });
        return await response.json();
    } catch (error) {
        console.error(`Error calling ${endpoint}:`, error);
        throw error;
    }
}
async function getData(endpoint) {
    try {
        const response = await fetch(`${baseURL}${endpoint}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        return await response;
    } catch (error) {
        console.error(`Error calling ${endpoint}:`, error);
        throw error;
    }
}
