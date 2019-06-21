$(document).ready(function () {
	let parts = window.location.search.substr(1).split("&");
	let $_GET = {};
	for (let i = 0; i < parts.length; i++) {
		let temp = parts[i].split("=");
		$_GET[decodeURIComponent(temp[0])] = decodeURIComponent(temp[1]);
	}

	/*--------Forms--------*/
	let passRegExp = new RegExp("^(((?=.*[a-z])(?=.*[0-9]))|((?=.*[A-Z])(?=.*[0-9])))(?=.{6,})");

	let registration = new Vue({
		el: "#signUp form",
		data: {
			errors: [],
			pass: null,
			repass: null,
			message: ""
		},
		methods: {
			checkForm() {
				this.errors = [];
				if (!this.pass.match(passRegExp))
					this.errors.push("Password must be at least of length 6 and contain letters and digits");
				else if (this.repass !== this.pass)
					this.errors.push("Password and Re-password must be equal");
				return this.errors.length === 0;
			},
			sendForm(e) {
				if (this.checkForm()) {
					axios({
						method: 'post',
						url: '/registration',
						data: new FormData(e.target)
					}).then((response) => {
						this.errors.push.apply(this.errors, response.data);
						if (!this.errors.length) {
							e.target.reset();
							this.message = "Registration is almost done! You should confirm your E-mail to log in."
						}
					}).catch(() => {
						this.errors.push("Something went wrong! Try again")
					});
				}
			}
		}
	});

	let login = new Vue({
		el: "#logIn form",
		data: {
			errors: [],
			message: ""
		},
		methods: {
			sendForm(e) {
				this.errors = [];
				axios({
					method: 'post',
					url: '/login',
					data: new FormData(e.target)
				}).then((response) => {
					this.errors.push.apply(this.errors, response.data);
					if (!this.errors.length) {
						location.reload()
					}
				}).catch(() => {
					this.errors.push("Something went wrong! Try again")
				});
			}
		}
	});

	let reset = new Vue({
		el: "#reset form",
		data: {
			action: "action" in $_GET && "email" in $_GET && "token" in $_GET ? $_GET["action"] : "check",
			email: null,
			pass: null,
			repass: null,
			errors: [],
			message: ""
		},
		created() {
			if ("action" in $_GET && $_GET["action"] == "reset") {
				$("#reset").modal("show");
				this.action = $_GET.action;
				this.email = $_GET["email"];
			}
		},
		methods: {
			checkForm(action) {
				this.errors = [];
				if (!this.pass || !this.repass)
					this.errors.push("Empty password");
				else if (!this.pass.match(passRegExp))
					this.errors.push("Password must be at least of length 6 and contain letters and digits");
				else if (this.repass !== this.pass)
					this.errors.push("Password and Re-password must be equal");
				return this.errors.length === 0;
			},
			sendForm(e) {
				this.errors = [];
				this.message = "";
				let data = new FormData(e.target);
				if (this.action === "reset") {
					if (!this.checkForm()) return;
					data.append("token", $_GET["token"]);
				}
				axios({
					method: 'post',
					url: '/reset',
					data: data
				}).then((response) => {
					e.target.reset();
					this.errors.push.apply(this.errors, response.data);
					if (!this.errors.length) {
						if (this.action === "check")
							this.message = "Letter with link to re-initialize your password was sent to your E-mail!"
						else if (this.action === "reset")
							location.replace(location.href.split('?')[0]);
					}
				}).catch(() => {
					this.errors.push("Something went wrong! Try again")
				});
			}
		}
	});

	let elem = document.querySelector(".profile__avatar input");
	if (elem) elem.onchange = (e) => {
		e.target.parentNode.classList.add("selected");
	};

	$('.multiple-tags').select2({
		placeholder: "Select some tags",
		tags: true
	});

	$('.likeUser').click(function () {
		axios.get(location.origin + '/like_user', {
			params: {
				liked_user: $(this).siblings(':first-child').text()
			}
		}).then(() => {
			$(this).attr('disabled', true)
		}).catch(() => {
			console.log("Something went wrong! Try again")
		});
	});
});
