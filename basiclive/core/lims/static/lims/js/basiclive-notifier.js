// heavily inspired by https://auct.github.io/b5toast
var blNotify = {
    createToastElement: function (html) {
        const template = document.createElement("template");
        html = html.trim();
        template.innerHTML = html;
        return template.content.firstChild;
    },
    show: function (params) {
        let toastContainer = document.getElementById("toast-container");
        if (!toastContainer) {
            toastContainer = document.createElement("div");
            toastContainer.id = "toast-container";
            toastContainer.className = "position-fixed bottom-0 end-0 p-3";
            document.body.appendChild(toastContainer);
        }
        let defaults = {
            theme: "light",     // default theme, can be "light" or "dark"
            color: "light",     // default background color, can be "light", "primary", "secondary", etc
            title: "",          // optional title
            message: "This is a toast message", // default message
            delay: 3000,        // default delay in milliseconds
            textColor: ""       // text-color, will be appended to "text-" to create a class like "text-white"
        };
        let options = Object.assign({}, defaults, params);
        let title = "";
        let closeBtn = '<button type="button" class="btn-close ms-auto me-1" data-bs-dismiss="toast" aria-label="Close"></button>';
        if (options.title) {
            title = `
                <div class="toast-header d-flex flex-row bg-transparent text-${options.textColor}">
                <strong>${options.title}</strong>${closeBtn}</div>
            `;
            closeBtn = ""; // if title is set, we don't need the close button in the body
        }
        const html = `
        <div data-bs-theme="${options.theme}" 
            class="toast d-flex flex-column align-items-stretch mt-1 text-${options.textColor} bg-${options.color} border-0" role="alert" 
            aria-live="assertive" aria-atomic="true">
            ${title}
            <div class="toast-body d-flex">
                <div>${options.message}</div>${closeBtn}
            </div>
        </div>`;
        const toastElement = blNotify.createToastElement(html);
        toastContainer.appendChild(toastElement);
        const toast = new bootstrap.Toast(toastElement, {
            delay: options.delay, animation: true
        });
        toast.show();
        setTimeout(() => toastElement.remove(), options.delay + 1000); // + 1 second for animation
    },
    error: function (parameters) {
        let options = Object.assign({'theme': 'dark', 'color': 'danger', 'textColor': 'white'}, parameters);
        blNotify.show(options);
    },
    success: function (parameters) {
        let options = Object.assign({'theme': 'dark', 'color': 'success', 'textColor': 'white'}, parameters);
        blNotify.show(options);
    },
    info: function (parameters) {
        let options = Object.assign({'theme': 'dark', 'color': 'info', 'textColor': 'white'}, parameters);
        blNotify.show(options);
    },
    warning: function (parameters) {
        let options = Object.assign({'theme': 'dark', 'color': 'warning', 'textColor': 'white'}, parameters);
        blNotify.show(options);
    }
};