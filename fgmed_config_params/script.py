users = self.env['res.users'].search([('login', '!=', '1')])
users[2].login = 'teste@gmail.com';
users[2].password = '123';
self.env.cr.commit();
#print(self.env['estate.property'].search([('name','=','test')])[0].date_availability)
