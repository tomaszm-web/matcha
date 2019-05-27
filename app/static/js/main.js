var form = new Vue({
	el: '#signUpForm',
	data: {
		errors: [],
		pass: null,
		repass: null,
		passRegExp: new RegExp("^(((?=.*[a-z])(?=.*[0-9]))|((?=.*[A-Z])(?=.*[0-9])))(?=.{6,})")
},
methods: {
	checkForm: function(e) {
		e.preventDefault();
		this.errors = [];
		if (!this.pass.match(this.passRegExp))
			this.errors.push("Password must be at least of length 6 and contain letters and digits");
		else if (this.repass !== this.pass)
			this.errors.push("Password and Re-password must be equal");
	}
}
});