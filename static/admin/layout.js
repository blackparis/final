document.addEventListener('DOMContentLoaded', () => {
    document.querySelector("#searchform").onsubmit = ()=> {
        if (!document.querySelector("#keyword").value) {
            alert("Type Something");
            return false;
        }
    };
});