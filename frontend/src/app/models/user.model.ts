export class User {
  username: string;
  email: string;
  password: string;
  pet_name: string;

  constructor(username: string, email: string, password: string, pet_name: string = "") {
    this.username = username;
    this.email = email;
    this.password = password;
    this.pet_name = pet_name;
  }

}