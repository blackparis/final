document.addEventListener('DOMContentLoaded', () => {
    document.querySelector("#loginForm").onsubmit = ()=> {
        if (!document.querySelector("#username").value) {
            alert("Enter a Username");
            return false;
        }
        if (!document.querySelector("#password").value) {
            alert("Enter a Password");
            return false;
        }            
    };
});

//also used for customer login