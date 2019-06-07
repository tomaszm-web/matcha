form = new Vue({
	el: '#signUpForm',
	data: {
		errors: [],
		pass: null,
		repass: null,
		passRegExp: new RegExp("^(((?=.*[a-z])(?=.*[0-9]))|((?=.*[A-Z])(?=.*[0-9])))(?=.{6,})"),
		message: null
	},
	methods: {
		checkForm() {
			this.errors = [];
			if (!this.pass.match(this.passRegExp))
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
				.then(function () {
					e.target.reset();
					this.message = "Registration is almost done! You should confirm your E-mail.";
				})
				.catch(function (error) {
					console.log(error);
				});
			}
		}
	}
});
