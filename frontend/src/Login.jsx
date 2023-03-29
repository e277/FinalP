import React, { useState } from 'react';

function LoginForm() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleLogin = async (event) => {
        event.preventDefault();

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
        <div className='flex flex-col h-screen'>
            <nav className='flex items-center justify-between text-slate-100 px-4 h-12 bg-red-500 w-full'>
                <span className='font-semibold text-xl'>OurVLE</span>
                <div className=''>
                    <form onSubmit={handleLogin} className='space-x-2'>
                        <input
                            type="text"
                            name='username'
                            placeholder='username'
                            value={e => setUsername(e.target.vaue)}
                            className='border-none outline-none rounded-sm p-1'
                        />
                        <input
                            type="password"
                            name='password'
                            placeholder='password'
                            value={e => setPassword(e.target.vaue)}
                            className='border-none outline-none rounded-sm p-1'
                        />
                        <button 
                            type='submit' onClick={handleLogin}
                            className='bg-slate-100 text-slate-900 rounded-sm p-1 '
                        >
                            Login</button>

                    </form>
                </div>
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
        </div>
    );
}

export default LoginForm;
