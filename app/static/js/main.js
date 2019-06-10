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
				})
				.then((response) => {
					e.target.reset();
					this.errors.push.apply(this.errors, response.data);
					if (!this.errors.length) {
						this.message = "Registration is almost done! You should confirm your E-mail to log in."
					}
				})
				.catch(() => {
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
			})
			.then((response) => {
				this.errors.push.apply(this.errors, response.data);
				if (!this.errors.length) {
					location.reload()
				}
			})
			.catch(() => {
				this.errors.push("Something went wrong! Try again")
			});
		}
	}
});

let reset = new Vue({
	el: "#reset form",
	data: {
		action: "check",
		pass: null,
		repass: null,
		errors: [],
		message: ""
	},
	methods: {
		checkForm(action) {
			this.errors = [];
			if (!this.pass.match(passRegExp))
				this.errors.push("Password must be at least of length 6 and contain letters and digits");
			else if (this.repass !== this.pass)
				this.errors.push("Password and Re-password must be equal");
			return this.errors.length === 0;
		},
		sendForm(e) {
			this.errors = [];
			this.message = "";
			if (this.action === "reset" && !this.checkForm()) return ;
			let data = new FormData(e.target);
			data.append("action", this.action);
			axios({
				method: 'post',
				url: '/reset',
				data: data
			})
			.then((response) => {
				e.target.reset();
				this.errors.push.apply(this.errors, response.data);
				if (!this.errors.length) {
					if (this.action === "check")
						this.message = "Letter with link to re-initialize your password was sent to your E-mail!"
					this.action = "reset"
				}
			})
			.catch(() => {
				this.errors.push("Something went wrong! Try again")
			});
		}
	}
});
