document.addEventListener('DOMContentLoaded', () => {

    document.querySelectorAll(".categories").forEach(a => {
        a.onclick = ()=> {
            let c = a.dataset.category;
            document.querySelectorAll(".products").forEach(div => {
                if (div.id === c) {
                    div.style.display = "block";
                } else {
                    div.style.display = "none";
                }
            });
            return false;
        }        
    });
    
    document.querySelector("#addtags").onclick = ()=> {

        const request = new XMLHttpRequest();
        request.open('GET', "/admin/newproducts");
        request.onload = () => {            
            let res = JSON.parse(request.responseText);
            if (res.success) {
                document.querySelectorAll(".products").forEach(r => {
                    let n = r.dataset.name;
                    let tag = `tags_${n}`;
                    if (document.getElementById(tag)) {
                        r.style.display = "none";
                    } else {
                        r.style.display = "block";
                    }
                });
            } else {
                alert("No New Products\nClick on Edit Tags to change existing tags.");
            }
        };
        request.send();
        return false;
    };

    document.querySelector("#return_addtags").onclick = ()=> {
        document.querySelectorAll(".products").forEach(r => {
            r.style.display = "block";
        });
        return false;
    };    
});