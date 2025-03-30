const registerUser = async (userData) => {
    try {
        const response = await fetch('http://localhost:4000/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Registration successful:', data);
        return data;
    } catch (error) {
        console.error('Registration failed:', error);
        throw error;
    }
};

// Example usage
const userData = {
    username: 'exampleUser',
    password: 'examplePassword',
    email: 'example@example.com',
};

registerUser(userData).catch((err) => console.error(err));