drop table if exists user;
create table user (
  user_id integer primary key autoincrement,
  email text not null,
  name text not null,
  pw_hash text not null,
  gender text not null,
  height text not null,
  top text not null,
  bottom text not null,
  bust text not null,
  shoe_size text not null
);


--insert into user values(1, '', '', '', '', '', '', '', '', '');

drop table if exists item;
create table item (
  item_id integer primary key autoincrement,
  item_name text not null,
  item_url text not null,
  item_picture_url text not null,
  merchant_id integer not null
);

drop table if exists merchant;
create table merchant (
  merchant_id integer primary key autoincrement,
  merchant_name text not null,
  merchant_url text not null,
  merchant_logo_url text not null  
);

drop table if exists review;
create table review (
  review_id integer primary key autoincrement,
  item_id integer not null,
  user_id integer not null,
  date integer,
  text text not null,
  size integer not null,
  length integer not null,
  thickness integer not null,
  quality integer not null,
  recommend integer not null
);





insert into item
  values (1, 'black jacket', 'http://google.com', 'http://images.asos-media.com/inv/media/2/4/1/1/3131142/black/image1xxl.jpg', 1);
insert into item
  values (2, 'berry dress', 'http://google.com', 'http://images.asos-media.com/inv/media/8/3/9/7/3287938/berry/image1xl.jpg', 1);
insert into item 
  values (3, 'black dress', 'http://google.com', 'http://images.asos-media.com/inv/media/9/6/9/9/3269969/black/image1xl.jpg', 1);
insert into item 
  values (4, 'mars print', 'http://google.com', 'http://images.asos-media.com/inv/media/8/6/6/0/3020668/marsprint/image1xl.jpg', 1);
insert into item 
  values (5, 'creamblack dress', 'http://google.com', 'http://images.asos-media.com/inv/media/4/5/8/7/3287854/creamblack/image1xl.jpg', 1);
insert into item 
  values (6, 'white dress', 'http://google.com', 'http://images.asos-media.com/inv/media/3/3/1/1/3221133/nude/image1xl.jpg', 1);
insert into item 
  values (7, 'black shirt', 'http://google.com', 'http://images.asos-media.com/inv/media/5/0/9/5/3145905/black/image1xl.jpg', 1);


insert into review
  values (1, 2, 1, 1, 'this berry dress is so cool!', 1, 1, 1, 1, 1);
insert into review
  values (2, 2, 1, 1, 'fits great!', 1, 1, 1, 1, 1);
insert into review
  values (3, 2, 2, 1, 'stylish!', 1, 1, 1, 1, 1);
insert into review
  values (4, 2, 3, 1, 'great!', 1, 1, 1, 1, 1);
