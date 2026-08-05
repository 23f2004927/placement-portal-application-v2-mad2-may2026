/*
  Single place to edit site-wide chrome text.
  Nothing here is fetched or reactive — it's plain data imported by the
  components that render it, so wording changes never touch markup.
*/

export const site = {
  name: 'Placement Portal V2',

  /*
    Rendered in the footer, joined with a middle dot.
    Add, remove or reorder freely — the footer just joins whatever is here.
  */
  footerMeta: [
    'Placement Portal V2',
    'Modern Application Development II — Project',
    'Roll No. 00f0000000',
    'Diploma Level',
  ],

  /*
    External profile links. These are real outbound URLs, so the footer renders
    them as plain <a> tags, not RouterLinks.
  */
  footerLinks: [
    { label: 'GitHub', url: 'https://github.com/your-handle' },
    { label: 'LinkedIn', url: 'https://www.linkedin.com/in/your-handle' },
  ],
}
