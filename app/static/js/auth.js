async function login(username, password) {
    const response = await fetch('/token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
    });
    
    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        return true;
    }
    return false;
}

// API 요청시 인증 헤더 추가
async function authenticatedFetch(url, options = {}) {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login';
        return;
    }
    
    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };
    
    return fetch(url, {...options, headers});
} 