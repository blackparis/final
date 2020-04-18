document.addEventListener('DOMContentLoaded', () => {
    document.querySelector("#address_form").onsubmit = ()=> {
        let name = document.querySelector("#name").value;
        let mobile = document.querySelector("#mobile").value;
        let address = document.querySelector("#address").value;
        let city = document.querySelector("#city").value;
        let pincode = document.querySelector("#pincode").value;
        let state = document.querySelector("#state").value;
        let country = document.querySelector("#country").value;

        if (!name) {
            alert("Type your Name");
            return false;
        } else if (!mobile) {
            alert("Type your Contact Number");
            return false;
        } else if (!address) {
            alert("Type your Address");
            return false;
        } else if (!city) {
            alert("Type your City");
            return false;
        } else if (!pincode) {
            alert("Type Pincode");
            return false;
        } else if (!state) {
            alert("Type your State");
            return false;
        } else if (!country) {
            alert("Type your Country");
            return false;
        }
    };
});