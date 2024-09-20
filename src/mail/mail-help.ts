// // require('dotenv').config();
// // const nodemailer = require('nodemailer');
// // const { EMAIL, EMAIL_PASSWORD } = process.env;

// const nodemailerConfig = {
//   host: 'smtp.ukr.net',
//   port: 465,
//   secure: true,
//   auth: {
//     user: EMAIL,
//     pass: EMAIL_PASSWORD,
//   },
// };

// const transport = nodemailer.createTransport(nodemailerConfig);
// // const data = {
// //   from: EMAIL,
// //   to: 'anneta.liss@gmail.com',
// //   subject: 'Test from Node.js',
// //   html: '<strong>Test Node</strong>',
// // };

// const sendEmail = data => {
//   const email = { ...data, from: EMAIL };
//   return transport.sendMail(email);
// };

// module.exports = sendEmail;
