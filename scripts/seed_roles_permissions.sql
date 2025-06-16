-- ===================================================================
-- seed_roles_permissions.sql
-- ===================================================================

-- 0) Truncate & reset all three tables
SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE RolePermission;
ALTER TABLE RolePermission AUTO_INCREMENT = 1;

TRUNCATE TABLE Permission;
ALTER TABLE Permission AUTO_INCREMENT = 1;

TRUNCATE TABLE Roles;
ALTER TABLE Roles AUTO_INCREMENT = 1;

SET FOREIGN_KEY_CHECKS = 1;


-- 1) Insert Roles
INSERT INTO Roles (RoleName, RoleDescription, created_at, updated_at)
VALUES
  ('candidate',  'Job seeker / candidate', NOW(), NOW()),
  ('recruiter',  'Individual recruiter',   NOW(), NOW()),
  ('Company HR','Company HR user',        NOW(), NOW());


-- 2) Insert Permissions
INSERT INTO Permission (PermissionName, Description, created_at, updated_at)
VALUES
  -- Candidate perms
  ('job.detailview',      'See job details',                         NOW(), NOW()),
  ('job.search',          'Search and filter job listings',           NOW(), NOW()),
  ('job.apply',           'Apply to a job',                           NOW(), NOW()),
  ('job.save',            'Save/bookmark a job for later',            NOW(), NOW()),
  ('application.view_own','View your submitted applications',         NOW(), NOW()),
  ('resume.upload',       'Upload a new resume file',                NOW(), NOW()),
  ('resume.select',       'Select one resume as active profile',      NOW(), NOW()),
  ('profile.change',      'Edit your own user profile',               NOW(), NOW()),
  ('auth.password_change','Change your password while logged in',     NOW(), NOW()),
  ('auth.password_reset', 'Request a password reset email',           NOW(), NOW()),

  -- Recruiter + Company HR perms
  ('job.view',            'See all job listings',                     NOW(), NOW()),
  ('job.create',          'Post a new job opening',                   NOW(), NOW()),
  ('job.update',          'Edit a job you have posted',               NOW(), NOW()),
  ('job.delete',          'Delete or archive a job you posted',       NOW(), NOW()),
  ('application.view_all','View all applicants for your jobs',        NOW(), NOW()),

  -- Company HR only
  ('company.view',        'View your company profile',                NOW(), NOW()),
  ('company.update',      'Update your company profile',              NOW(), NOW()),
  ('talent.onboard',      'Onboard a candidate to your company',      NOW(), NOW());


-- 3) Map Permissions → Roles

-- candidate (RoleID = 1)
INSERT INTO RolePermission (role_id, permission_id)
SELECT
  (SELECT RoleID FROM Roles WHERE RoleName='candidate'),
   PermissionID
FROM Permission
WHERE PermissionName IN (
  'job.detailview','job.search','job.apply','job.save',
  'application.view_own',
  'resume.upload','resume.select',
  'profile.change',
  'auth.password_change','auth.password_reset'
);

-- recruiter (RoleID = 2)
INSERT INTO RolePermission (role_id, permission_id)
SELECT
  (SELECT RoleID FROM Roles WHERE RoleName='recruiter'),
   PermissionID
FROM Permission
WHERE PermissionName IN (
  'job.view','job.create','job.update','job.delete',
  'application.view_all',
  'auth.password_change','auth.password_reset'
);

-- Company HR (RoleID = 3)
INSERT INTO RolePermission (role_id, permission_id)
SELECT
  (SELECT RoleID FROM Roles WHERE RoleName='Company HR'),
   PermissionID
FROM Permission
WHERE PermissionName IN (
  'job.view','job.create','job.update','job.delete',
  'application.view_all',
  'company.view','company.update','talent.onboard',
  'auth.password_change','auth.password_reset'
);
