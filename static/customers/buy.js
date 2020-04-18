document.addEventListener('DOMContentLoaded', () => {

    document.querySelector("#orderconfirmation").onsubmit = ()=> {        
        var address = false;
        document.querySelectorAll(".address").forEach(r => {
            if (r.checked === true) {
                address = r.value;
            }
        })

        if (address === false) {
            alert("Select a Delivery Address");
            return false;
        }

        let time = document.querySelector("#time").value;

        var csrftoken = getCookie('csrftoken');
        const request = new XMLHttpRequest();
        request.open('POST', "/buy");
        request.setRequestHeader("X-CSRFToken", csrftoken);

        request.onload = () => {
            let res = JSON.parse(request.responseText);
            if (res.success) {
                document.querySelector("#confirmationmessage").innerHTML = "";
                let message = `Your Order is Confirmed.\nTransaction ID: ${res.message}`;
                alert(message);                
                location.reload();
            } else {
                alert(res.message);
            }
        };

        const order = new FormData();
        order.append('address', address);
        order.append('time', time);
        request.send(order);
        document.querySelector("#confirmbutton").disabled = true;
        document.querySelector("#confirmationmessage").innerHTML = "Please Wait";
        return false;
    };
});

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}