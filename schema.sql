drop table if exists sneakers;
create table sneakers (
  id integer primary key autoincrement,
  name text not null,
  slug text not null,
  description text not null
);