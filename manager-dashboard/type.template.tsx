/*
   Both lint and build steps fail if `generated/type.tsx` is missing
   We generally genereate this file using graphql-codegen but graphql-codegen
   cannot always be used.
   In such cases, just copy this mock type.tsx to ensure that lint and build
   steps pass.
  NOTE: typecheck step still fails.
*/

export type Query = {
  __typename?: 'Query';
};

export type Mutation = {
  __typename?: 'Mutation';
};
