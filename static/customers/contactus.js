document.addEventListener('DOMContentLoaded', () => {
    document.querySelector("#contactform").onsubmit = ()=> {
        var name = document.querySelector("#name").value;
        if (!name) {
            alert("Your Name?");
            return false;
        }

        var subject = document.querySelector("#subject").value;
        if (!subject) {
            alert("Subject?");
            return false;
        }

        var message = document.querySelector("#message").value;
        if (!message) {
            alert("Message?");
            return false;
        }
        
        const request = new XMLHttpRequest();
        request.open('POST', '/contactus');
        request.onload = () => {
            const res = JSON.parse(request.responseText);
                if (res.success) {
                    document.querySelector("#contactus").remove();
                    document.querySelector("#contactmessage").innerHTML = "Thank you for contacting us. We will revert back to you shortly.";
                }
                else {
                    alert(res.message);
                    document.getElementById("submitbutton").disabled = false;
                    document.querySelector("#submitmessage").innerHTML = "";
                }
        };

        const data = new FormData();
        data.append('name', name);
        data.append('subject', subject);
        data.append('message', message);
        request.send(data);
        document.getElementById("submitbutton").disabled = true;
        document.querySelector("#submitmessage").innerHTML = "please wait";
        return false;
    };    
});