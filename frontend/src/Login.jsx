import React, { useState } from 'react';

function LoginForm() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = async (event) => {
        event.preventDefault();
        console.log('Logging in with username: ' + username + ' and password: ' + password)

        // Call the Flask API to authenticate the user
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        if (response.ok) {
            const data = await response.json();

            // TODO: Store the JWT token in the browser's localStorage
        } else {
            const error = await response.json();
            console.error(error);
        }
    };

    return (
        <>
            <nav className='h-12 px-4 text-white bg-red-500 flex items-center justify-between'>
                <div className='font-medium tracking-wide'>OurVLE</div>
                <form onSubmit={handleLogin} className='space-x-2'>
                    <input
                        type="text"
                        placeholder='username'
                        onChange={(event) => setUsername(event.target.value)}
                        className='border-none outline-none rounded-sm text-slate-900 p-1 text-sm'
                        />
                    <input
                        type="password"
                        placeholder='password'
                        onChange={(event) => setPassword(event.target.value)}
                        className='border-none outline-none rounded-sm text-slate-900 p-1 text-sm'
                        />
                    <button 
                        type='submit' onClick={handleLogin}
                        className='bg-slate-100 text-slate-600 rounded-sm p-1 text-sm'
                        >
                        Login
                    </button>
                </form>
            </nav>
            {/* <div className='h-full'>
                <form onSubmit={handleLogin} className='text-slate-900 bg-slate-300 flex flex-col items-center justify-center'>
                
                <input
                type="text"
                id="username"
                value={username}
                        onChange={(event) => setUsername(event.target.value)}
                    />

                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(event) => setPassword(event.target.value)}
                        />
                        
                        <button type="submit">Login</button>
                        </form>
                    </div> */}
        </>
    );
}

export default LoginForm;
