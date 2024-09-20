import { MailerService } from '@nestjs-modules/mailer';
import { Injectable } from '@nestjs/common';

@Injectable()
export class MailService {
  constructor(private readonly mailerService: MailerService) {}

  sendEmail(to: string, subject: string, html: string) {
    return this.mailerService.sendMail({
      to,
      subject,
      html,
    });
  }

  sendWelcome(to: string) {
    return this.sendEmail(to, 'Thanks for reg to my backend', '<p>Thanks!</p>');
  }
}
