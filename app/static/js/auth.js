const signIn = document.getElementById('signIn');
signIn.addEventListener('click', async (e) => {
    e.preventDefault();
    signIn.innerHTML = "Signing in...";
    signIn.disabled = true;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    try{
        const response = await fetch("/auth/login-user", {
            method: 'POST',
            headers: {
                "Content-Type" : "application/json"
            },
            credentials: "same-origin",
            body: JSON.stringify({
                email: email,
                password: password
            })
        })
        const result = await response.json();
        if (response.ok){
            window.location.href = result.redirect;
            console.log("Login successful:", result.message);
        }
        else{
            console.log("login failed:", response.status + " " + result.error);
        }
    }
    catch(error){
        console.error("Network error: ", error);
    }
});